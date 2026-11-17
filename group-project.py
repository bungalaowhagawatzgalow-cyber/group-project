'''Group Project''' is a joke esoteric programming language where programs are
group chat transcripts. Five fixed users participate.

== The Cast ==

{| class="wikitable"
|-
! User !! Role
|-
| '''@me'''
| Does all the work. Variables, arithmetic, print, functions, if/else. Unrecognized lines are ignored (talking).
|-
| '''@slacker'''
| Fixed list of non-answers. No mechanical purpose.
|-
| '''@deadline'''
| Controls loops.
|-
| '''@prof'''
| Final line only. Receives output.
|-
| '''@parent'''
| Debug and panic button.
|}

== Getting Started ==

<pre>
curl -o group-project.py https://raw.githubusercontent.com/YOUR_USER/group-project/main/group-project.py
python group-project.py program.slacker
</pre>

* Extension: <code>.slacker</code>
* Errors: <code>[line N]</code> prefix, exit code 1
* Requires Python 3.6+, no dependencies

== Syntax ==

<pre>
@user: message
</pre>

=== @me ===
<pre>
@me: x is 5                # assignment
@me: y is x + 3            # arithmetic
@me: print x               # print
@me: print "hello"         # string
@me: read n                # input
@me: x is "hi" + " there"  # string concat
@me: x is 17 mod 5         # modulo
@me: x is sqrt of 144      # math
@me: x is pi               # constant
@me: x is 5 greater than 3 and 2 less than 4  # logic
</pre>

Anything else @me says is ignored.

=== Functions ===
<pre>
@me: new task: greet(name)
@me: print "hi " + name
@me: task done
@me: do greet("world")
</pre>

No recursion. Local scope.

=== If / else ===
<pre>
@me: if x greater than 5 then
@me: print "big"
@me: else
@me: print "small"
@me: end
</pre>

No nesting.

=== @slacker ===

<pre>
ok
cool
when is it due
can we just do it in a group
I'll do the intro
brb
ty
lmao
I'll send it later
sounds good
make sure to add my name
</pre>

Mandatory after certain @deadline commands:

{| class="wikitable"
|-
! After !! Must say
|-
| <code>due in N</code>
| <code>when is it due</code>
|-
| <code>not done until</code>
| <code>brb</code>
|-
| <code>done</code>
| <code>I'll send it later</code>
|}

=== @deadline ===
<pre>
@deadline: due in 5               # for loop
@deadline: not done until x is 10  # while loop
@deadline: done                    # end loop
</pre>

Nested loops supported.

=== @parent ===

{| class="wikitable"
|-
! Says !! Does
|-
| <code>are you guys done yet</code>
| Nothing
|-
| <code>what's the progress</code>
| Prints all variables
|-
| <code>finish this or you're grounded</code>
| Kills program
|}

=== @prof ===
<pre>
@prof: here's our answer: x
</pre>

Must be final line. Only once.

== Rules ==
* 1 @slacker per 4 @me messages or warning
* @prof final line, only once
* @slacker and @parent can't repeat same message in a row
* Mandatory slacker responses after @deadline commands
* No nested ifs, no recursion
* Unrecognized @me lines ignored

== Examples ==

=== Counting to 5 ===
<pre>
@me: ok so the prof said we need to count to 5
@slacker: ok
@me: x is 0
@deadline: due in 5
@slacker: when is it due
@me: print x
@me: x is x + 1
@slacker: cool
@me: print x
@me: x is x + 1
@parent: are you guys done yet
@me: no
@me: print x
@me: x is x + 1
@slacker: sounds good
@me: print x
@me: x is x + 1
@deadline: done
@slacker: I'll send it later
@me: phew
@prof: here's our answer: x
</pre>
<pre>
0
1
2
3
4
5
</pre>

=== If / else ===
<pre>
@me: so the question is like 7 right
@slacker: lmao
@me: x is 7
@me: if x greater than 5 then
@me: print "big"
@me: else
@me: print "small"
@me: end
@slacker: cool
@parent: what's the progress
@me: done actually
@prof: here's our answer: x
</pre>
<pre>
big
7
</pre>

=== Function ===
<pre>
@me: i made a thing that doubles numbers
@slacker: can we just do it in a group
@me: new task: double(n)
@me: print n * 2
@me: task done
@slacker: I'll do the intro
@me: do double(21)
@slacker: ty
@parent: are you guys done yet
@me: yeah
@prof: here's our answer: x
</pre>
<pre>
42
0
</pre>

== Operations ==

{| class="wikitable"
|-
! Category !! Values
|-
| Operators
| <code>+</code> <code>-</code> <code>*</code> <code>/</code> <code>mod</code>
|-
| Logic
| <code>and</code> <code>or</code> <code>not</code>
|-
| Functions
| <code>sqrt of</code> <code>cbrt of</code> <code>abs of</code> <code>floor of</code> <code>ceil of</code> <code>log of</code> <code>sin of</code> <code>cos of</code> <code>tan of</code>
|-
| Constants
| <code>pi</code> <code>e</code>
|-
| Comparisons
| <code>greater than</code> <code>less than</code> <code>equals</code> <code>not equals</code> <code>greater than or equal to</code> <code>less than or equal to</code>
|}

== Limitations ==
* No recursion, arrays, string indexing, nested ifs, float literals in loop conditions

== Implementation ==
Python 3, single file. [[File:group-project.py]] (public domain)

[[Category:Languages]]
[[Category:Implemented]]
[[Category:Joke languages]]   