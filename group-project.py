import sys
import math

CONFIG = {
    'users': {
        'me': '@me',
        'slacker': '@slacker',
        'deadline': '@deadline',
        'prof': '@prof',
        'parent': '@parent',
    },

    'slacker_lines': {
        'ok', 'cool', 'when is it due', 'can we just do it in a group',
        "i'll do the intro", 'brb', 'ty', 'lmao',
        "i'll send it later", 'sounds good', 'make sure to add my name'
    },

    'parent_lines': {
        'are you guys done yet',
        "what's the progress",
        "finish this or you're grounded",
    },

    'mandatory_slack': {
        'due in': 'when is it due',
        'not done until': 'brb',
        'done': "i'll send it later",
    },

    'errors': {
        'slacker_off_list': "{slacker}: {msg}\n{me}: bro that's not even one of your words",
        'slacker_repeat': "{slacker}: {msg}\n{slacker}: {msg}\n{me}: you literally just said that",
        'slacker_mandatory': "{slacker}: {msg}\n{me}: no, say the other thing, the one you always say at this point",
        'parent_off_list': "{parent}: {msg}\n{me}: mom, that's not how this works",
        'parent_repeat': "{parent}: {msg}\n{parent}: {msg}\n{me}: MOM stop",
        'due_not_number': "{deadline}: due in WHAT\n{me}: that's not a number, what do you mean",
        'due_negative': "{deadline}: due in {n}\n{me}: that's already passed, we're late",
        'done_no_loop': "{deadline}: done\n{me}: done with what, there's nothing running",
        'deadline_unknown': "{deadline}: {msg}\n{me}: you only get to say three things, pick one",
        'prof_twice': "{prof}: I said once\n{me}: we're not redoing this",
        'prof_bad_format': "{prof}: {msg}\n{prof}: I didn't ask for that, I asked for the answer",
        'unknown_user': "{user}: {msg}\n{me}: you're not in this group chat",
        'empty_file': "{me}: ...you sent me nothing\n{slacker}: when is it due\n{me}: I don't know",
        'no_submit': "{prof}: where's the answer\n{slacker}: I'll send it later\n{prof}: that's not an answer",
        'bad_varname': "{me}: {msg}\n{me}: that's not a name for a variable, use one word",
        'undefined_var': "{me}: {e}\n{me}: we never set that, where did you get that from",
        'div_zero': "{me}: you can't do that\n{slacker}: can we just do it in a group\n{me}: NO",
        'mod_zero': "{me}: same problem, you can't do that\n{slacker}: brb\n{me}: don't brb",
        'sqrt_neg': "{me}: that's not a real number\n{slacker}: sounds good\n{me}: it's not",
        'log_bad': "{me}: you can't log that\n{slacker}: ty\n{me}: there's nothing to thank me for",
        'if_nested': "{me}: one if at a time\n{slacker}: when is it due\n{me}: that's not helpful",
        'else_no_if': "{me}: else what, there's no if",
        'end_nothing': "{me}: end what, nothing's open",
        'task_nested': "{me}: you're already in one, finish it",
        'task_no_parens': "{me}: {msg}\n{me}: you forgot the part where you say what it takes",
        'task_done_no_task': "{me}: task done\n{me}: there's no task, you're not done with anything",
        'do_not_found': "{me}: {fname}\n{me}: we never made that, you're making things up",
        'do_bad_args': "{me}: {fname} takes {expected}, you gave {got}\n{me}: count your fingers",
        'do_no_parens': "{me}: {msg}\n{me}: you forgot the part where you say what it takes",
        'while_undef': "{me}: {v}\n{me}: we never set that, it doesn't exist yet",
        'slacker_warning': "{me}: you know what, I'll just do it myself\n{slacker}: brb",
    },
}


def err(key, line, **kw):
    u = CONFIG['users']
    msg = CONFIG['errors'][key].format(me=u['me'], slacker=u['slacker'], deadline=u['deadline'], prof=u['prof'], parent=u['parent'], **kw)
    print(f"[line {line}]")
    print(msg)
    sys.exit(1)


def run(lines):
    st = {}
    mc = 0
    slack = 0
    last_slack = ''
    pending_slack = None
    loop_stack = []
    loop_body = []
    in_if = False
    in_else = False
    if_body = []
    else_body = []
    if_var = ''
    if_cond = ''
    in_func = False
    func_name = ''
    func_params = []
    func_body = []
    funcs = {}
    submitted = False
    prof_count = 0
    total_lines = 0
    ln = 0
    u = CONFIG['users']

    for raw in lines:
        line = raw.strip()
        if not line or ':' not in line:
            continue
        ln += 1
        total_lines += 1
        user, msg = line.split(':', 1)
        user = user.strip().lstrip('@').lower()
        msg = msg.strip()

        if user == 'slacker':
            if pending_slack and msg.lower() != pending_slack:
                err('slacker_mandatory', ln, msg=msg, required=pending_slack)
            if msg.lower() not in CONFIG['slacker_lines']:
                err('slacker_off_list', ln, msg=msg)
            if msg.lower() == last_slack:
                err('slacker_repeat', ln, msg=msg)
            pending_slack = None
            last_slack = msg.lower()
            slack += 1
            if loop_stack: loop_body.append((user, msg, ln))
            if in_if:
                if in_else: else_body.append((user, msg, ln))
                else: if_body.append((user, msg, ln))
            if in_func: func_body.append((user, msg, ln))
            continue

        if user == 'parent':
            if msg.lower() not in CONFIG['parent_lines']:
                err('parent_off_list', ln, msg=msg)
            if msg.lower() == last_slack:
                err('parent_repeat', ln, msg=msg)
            if msg.lower() == "what's the progress":
                for k, v in st.items():
                    print(f"  {k} = {v}")
            elif msg.lower() == "finish this or you're grounded":
                print(f"{u['parent']}: finish this or you're grounded")
                sys.exit(1)
            continue

        if user == 'deadline':
            if msg.startswith('due in '):
                try:
                    n = int(msg.split('due in ')[1])
                except ValueError:
                    err('due_not_number', ln)
                if n <= 0:
                    err('due_negative', ln, n=n)
                loop_stack.append({'mode': 'for', 'n': n})
                loop_body = []
                pending_slack = CONFIG['mandatory_slack']['due in']
            elif msg.startswith('not done until '):
                p = msg.split(' is ')
                if len(p) < 2:
                    err('deadline_unknown', ln, msg=msg)
                wv = p[0].replace('not done until ', '').strip()
                wc = p[1].strip()
                loop_stack.append({'mode': 'while', 'wv': wv, 'wc': wc})
                loop_body = []
                pending_slack = CONFIG['mandatory_slack']['not done until']
            elif msg == 'done':
                if not loop_stack:
                    err('done_no_loop', ln)
                top = loop_stack.pop()
                pending_slack = CONFIG['mandatory_slack']['done']
                if top['mode'] == 'for':
                    for _ in range(top['n']):
                        for uu, mm, ll in loop_body:
                            if uu == 'me': execute_line(mm, st, ll, funcs)
                else:
                    while eval_cond(top['wv'], top['wc'], st, ln):
                        for uu, mm, ll in loop_body:
                            if uu == 'me': execute_line(mm, st, ll, funcs)
            else:
                err('deadline_unknown', ln, msg=msg)
            continue

        if user == 'prof':
            prof_count += 1
            if prof_count > 1:
                err('prof_twice', ln)
            if not msg.startswith("here's our answer:"):
                err('prof_bad_format', ln, msg=msg)
            print(eval_expr(msg.replace("here's our answer:", '').strip(), st, ln, funcs))
            submitted = True
            continue

        if user == 'me':
            mc += 1
            if mc % 4 == 0 and slack == 0:
                print(CONFIG['errors']['slacker_warning'].format(
                    me=u['me'], slacker=u['slacker'], deadline=u['deadline'], prof=u['prof'], parent=u['parent']))
                slack = 0

            if msg.startswith('new task: '):
                if in_func:
                    err('task_nested', ln)
                p = msg.replace('new task: ', '').strip()
                if '(' not in p or ')' not in p:
                    err('task_no_parens', ln, msg=msg)
                func_name = p.split('(')[0].strip()
                params_str = p.split('(')[1].rstrip(')')
                func_params = [x.strip() for x in params_str.split(',') if x.strip()]
                in_func = True
                func_body = []
                continue
            if msg == 'task done':
                if not in_func:
                    err('task_done_no_task', ln)
                funcs[func_name] = {'params': func_params, 'body': func_body}
                in_func = False
                continue

            if msg.startswith('if '):
                if in_if:
                    err('if_nested', ln)
                in_if = True
                in_else = False
                if_body = []
                else_body = []
                p = msg.replace('if ', '').replace(' then', '').strip().split()
                if len(p) >= 2:
                    if_var = p[0]
                    if_cond = ' '.join(p[1:])
                continue
            if msg == 'else':
                if not in_if:
                    err('else_no_if', ln)
                in_else = True
                continue
            if msg == 'end':
                if in_if:
                    in_if = False
                    in_else = False
                    cond = eval_cond_str(if_cond, st, ln)
                    chosen = if_body if cond else else_body
                    for uu, mm, ll in chosen:
                        if uu == 'me': execute_line(mm, st, ll, funcs)
                    continue
                err('end_nothing', ln)

            if in_func:
                func_body.append((user, msg, ln))
                continue
            if in_if:
                if in_else: else_body.append((user, msg, ln))
                else: if_body.append((user, msg, ln))
                continue
            if loop_stack:
                loop_body.append((user, msg, ln))
                continue
            execute_line(msg, st, ln, funcs)
            continue

        err('unknown_user', ln, user=f'@{user}', msg=msg)

    if total_lines == 0:
        err('empty_file', 0)
    if not submitted:
        err('no_submit', ln)


def execute_line(msg, st, ln, funcs):
    if msg.startswith('print '):
        print(eval_expr(msg[6:].strip(), st, ln, funcs))
        return
    if msg.startswith('read '):
        v = msg[5:].strip()
        if not v.isidentifier():
            err('bad_varname', ln, msg=msg, v=v)
        try:
            st[v] = int(input())
        except ValueError:
            try:
                st[v] = float(input())
            except ValueError:
                st[v] = input()
        return
    if msg.startswith('do '):
        p = msg[3:].strip()
        if '(' not in p or ')' not in p:
            err('do_no_parens', ln, msg=msg)
        fname = p.split('(')[0].strip()
        args_str = p.split('(')[1].rstrip(')')
        args = [x.strip() for x in args_str.split(',') if x.strip()]
        if fname not in funcs:
            err('do_not_found', ln, fname=fname)
        f = funcs[fname]
        if len(args) != len(f['params']):
            err('do_bad_args', ln, fname=fname, args=', '.join(args), expected=len(f['params']), got=len(args))
        local = dict(st)
        for i, param in enumerate(f['params']):
            local[param] = eval_expr(args[i], st, ln, funcs)
        for uu, mm, ll in f['body']:
            if uu == 'me': execute_line(mm, local, ll, funcs)
        st.update(local)
        return
    if ' is ' in msg:
        v, e = msg.split(' is ', 1)
        v = v.strip()
        if not v.isidentifier():
            err('bad_varname', ln, msg=msg, v=v)
        st[v] = eval_expr(e.strip(), st, ln, funcs)
        return
    return


def eval_expr(e, st, ln, funcs):
    e = e.strip()
    if e.startswith('"') and e.endswith('"'):
        return e[1:-1]

    if e == 'pi': return math.pi
    if e == 'e': return math.e

    for fn in ('sqrt', 'cbrt', 'abs', 'floor', 'ceil', 'log', 'sin', 'cos', 'tan'):
        if e.startswith(fn + ' of '):
            arg = eval_expr(e[len(fn) + 4:], st, ln, funcs)
            if fn == 'sqrt':
                if arg < 0:
                    err('sqrt_neg', ln, arg=arg)
                return math.sqrt(arg)
            if fn == 'cbrt':
                return math.copysign(abs(arg) ** (1/3), arg)
            if fn == 'abs':
                return abs(arg)
            if fn == 'floor':
                return math.floor(arg)
            if fn == 'ceil':
                return math.ceil(arg)
            if fn == 'log':
                if arg <= 0:
                    err('log_bad', ln, arg=arg)
                return math.log(arg)
            if fn == 'sin': return math.sin(arg)
            if fn == 'cos': return math.cos(arg)
            if fn == 'tan': return math.tan(arg)

    if ' mod ' in e:
        a, b = e.split(' mod ', 1)
        av, bv = eval_expr(a.strip(), st, ln, funcs), eval_expr(b.strip(), st, ln, funcs)
        if bv == 0:
            err('mod_zero', ln)
        return av % bv

    if e.startswith('not '):
        v = eval_expr(e[4:], st, ln, funcs)
        return int(v == 0)
    if ' and ' in e:
        a, b = e.split(' and ', 1)
        av, bv = eval_expr(a.strip(), st, ln, funcs), eval_expr(b.strip(), st, ln, funcs)
        return int(bool(av) and bool(bv))
    if ' or ' in e:
        a, b = e.split(' or ', 1)
        av, bv = eval_expr(a.strip(), st, ln, funcs), eval_expr(b.strip(), st, ln, funcs)
        return int(bool(av) or bool(bv))

    for cmp in ('greater than or equal to', 'less than or equal to', 'greater than', 'less than', 'not equals', 'equals'):
        if ' ' + cmp + ' ' in e:
            parts = e.split(' ' + cmp + ' ')
            if len(parts) == 2:
                a, b = eval_expr(parts[0].strip(), st, ln, funcs), eval_expr(parts[1].strip(), st, ln, funcs)
                if cmp == 'greater than': return int(a > b)
                if cmp == 'less than': return int(a < b)
                if cmp == 'equals': return int(a == b)
                if cmp == 'not equals': return int(a != b)
                if cmp == 'greater than or equal to': return int(a >= b)
                if cmp == 'less than or equal to': return int(a <= b)

    for op in ('+', '-', '*', '/'):
        if op in e:
            a, b = e.split(op, 1)
            av, bv = eval_expr(a.strip(), st, ln, funcs), eval_expr(b.strip(), st, ln, funcs)
            if op == '+':
                if isinstance(av, str) or isinstance(bv, str):
                    return str(av) + str(bv)
                return av + bv
            if op == '/' and bv == 0:
                err('div_zero', ln)
            if op == '-': return av - bv
            if op == '*':
                if isinstance(av, str) or isinstance(bv, str):
                    return str(av) * int(bv) if isinstance(bv, int) else str(av)
                return av * bv
            if op == '/': return av / bv

    return num(e, st, ln)


def num(e, st, ln):
    e = e.strip()
    try:
        return int(e)
    except ValueError:
        pass
    try:
        return float(e)
    except ValueError:
        pass
    if e in st:
        return st[e]
    err('undefined_var', ln, e=e)
    return 0


def eval_cond_str(c, st, ln):
    c = c.strip()
    for cmp in ('greater than or equal to', 'less than or equal to', 'greater than', 'less than', 'not equals', 'equals'):
        if cmp in c:
            parts = c.split(cmp)
            a, b = eval_expr(parts[0].strip(), st, ln, {}), eval_expr(parts[1].strip(), st, ln, {})
            if cmp == 'greater than': return a > b
            if cmp == 'less than': return a < b
            if cmp == 'equals': return a == b
            if cmp == 'not equals': return a != b
            if cmp == 'greater than or equal to': return a >= b
            if cmp == 'less than or equal to': return a <= b
    return False


def eval_cond(v, c, st, ln):
    if v not in st:
        err('while_undef', ln, v=v)
    return eval_cond_str(c, st, ln)


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        run(f.readlines())   
