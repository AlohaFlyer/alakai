# SAT Notes Ep 9: Lines Are Rates
cast: lehua, derek, pono, kaden
topic: Linear equations, slope as rate, systems, plug in and backsolve
facts: Linear equations, linear functions, and systems of linear equations are SAT Math Algebra skills (College Board skill list, satsuite.collegeboard.org/sat/whats-on-the-test/math; data/sat/skills.json ids math-alg-linear-fn, math-alg-linear-eq, math-alg-systems); in y = mx + b, m is the slope (rate of change) and b is the starting value or y-intercept (standard algebra); slope-and-start steps from data/strategies.json math-alg-linear-fn; backsolve (start with a middle choice) and pick-your-own-numbers steps from data/strategies.json general backsolve and plug-in; Math 2 modules x 22 questions x 35 minutes (College Board); app trap names "calculation slip" and "opposite" from assets/engine.js; Desmos systems method recalled from Ep 4; worked example arithmetic: 3 x 8 = 24, 40 - 24 = 16, check 16 + 24 = 40; backsolve arithmetic: 40 - 3(8) = 16, 40 - 3(10) = 10; plug-in arithmetic with t = 2: 3 x 2 = 6 gallons drained, 40 - 3(2) = 34 (target), 40 + 3(2) = 46 (miss); 35 minutes x 60 / 22 questions = about 95 seconds per Math question; examples are original items written for the show; Wednesday food trucks at the stables (cast.json places, Pukalani Stables food trucks on Wednesdays, no hours stated)
target_minutes: 8
homework: Drill linear functions | drill.html?skill=math-alg-linear-fn

LEHUA: Hey, welcome back to SAT Notes, episode nine. I'm Lehua. Derek is here, Coach Pono is here, and Kaden is here, and he drove himself today.
KADEN: I drove myself. My gas light came on in the parking lot. Every mile, the tank goes down the same amount, and so does my bank account.
DEREK: That's a linear function. You just taught the first half of the episode.
LEHUA: Hold that. Callback first. Kaden, last episode was transitions. What do you do before you look at the choices?
KADEN: Name the relationship. Add, contrast, cause, example, or sequence. Then cut every choice from the wrong category. The trap was opposite, like picking therefore when the team practiced and still lost.
PONO: Good. Today we're back to math, but the habit is the same. Say what's going on before you start moving.
LEHUA: Lines are rates. Derek.
DEREK: Here's the whole idea in one sentence. Almost every linear word problem on the SAT is a starting amount plus a rate. Something starts somewhere, and it changes by the same amount every step. That's a line.
DEREK: In y equals m x plus b, b is where you start. That's the y-intercept. And m is the rate, how much y changes every time x goes up by one. That's the slope. Here's the habit. Say the slope in words, with units. Not "slope is negative three." Say "negative three gallons per minute." If you can say it in words, you understand the problem.
KADEN: Why does saying it out loud matter?
DEREK: Because the most common mistake on these is swapping the slope and the starting value. If you say the units, you can hear which number is which. Forty gallons is an amount. Three gallons per minute is a rate.
PONO: Okay, let's try one. I'll read it twice. Short one.
PONO: "A water tank holds forty gallons. It drains at three gallons per minute. How many gallons are left after eight minutes?" A, sixteen. B, twenty-six. C, thirty-seven. D, sixty-four.
PONO: One more time. "A water tank holds forty gallons. It drains at three gallons per minute. How many gallons are left after eight minutes?" A, sixteen. B, twenty-six. C, thirty-seven. D, sixty-four.
LEHUA: Pause it and try. Find the start and the rate first.
LEHUA: And we're back. Kaden?
KADEN: Start is forty. Rate is negative three gallons per minute. So it's forty minus three times eight. Three times eight is twenty-four. Forty minus twenty-four is twenty-six. B.
DEREK: Your setup is perfect. Do the last subtraction again, slowly.
KADEN: Forty minus twenty-four. Zero minus four, I can't, so I borrow. Ten minus four is six. Then three minus two is one. Sixteen. Oh, come on.
DEREK: The answer is A, sixteen. And that's the trap. The app calls it calculation slip. You knew exactly what to do, and one small arithmetic step went wrong. Twenty-six is sitting there as choice B because borrowing and then forgetting to lower the tens digit is a common slip.
PONO: And look at the other two. Thirty-seven is forty minus three. That's one minute, not eight. Sixty-four is forty plus twenty-four. That's adding when the tank drains.
DEREK: Here's the fix for calculation slip. Check by going backward. If sixteen is left and twenty-four drained out, sixteen plus twenty-four should be forty. It is. Twenty-six plus twenty-four is fifty, which is more water than the tank started with. That check takes three seconds.
KADEN: So the check is just doing it in reverse.
DEREK: Right. Subtraction, check with addition. Division, check with multiplication. Or type it into Desmos if it's messy.
LEHUA: Now, backsolving. What's that?
DEREK: When the choices are numbers and the question asks for a value, you can test the choices instead of solving. Start with a middle choice, because if it's too big or too small, you know which way to move.
DEREK: Same tank. Say the question is, "After how many minutes will ten gallons be left?" And the choices are six, eight, ten, and twelve. Start with eight. Forty minus three times eight is sixteen. Sixteen gallons is too much water left, so you need more time. Move up. Try ten. Forty minus thirty is ten. Done. Ten minutes.
PONO: That's how you work a young horse. You don't guess the whole trail. You try one step, you see if he goes left or right, and you adjust.
KADEN: Coach, there's always a horse.
PONO: There's always a horse.
LEHUA: And plugging in?
DEREK: That one is for when the answer choices have letters in them. Pick a simple number, like two or three, for the letter. Work the problem with your number to get a target. Then put the same number into each choice and see which one hits the target.
DEREK: Same tank. Say the question asks which expression gives the gallons left after t minutes. Pick t equals two. Two minutes drains six gallons, so thirty-four are left. That's the target. Now test the choices. Forty minus three t, with t equals two, is thirty-four. Hit. Forty plus three t is forty-six. Miss. It turns algebra into arithmetic.
LEHUA: And systems?
DEREK: Two lines, two rates. Like two tanks draining at different speeds, and the question is when they hold the same amount. That's where the lines cross. Episode four has the whole Desmos method. Type both, tap where they cross, and read the part they asked for.
KADEN: Okay, how do I know which number is the slope when it's a graph?
DEREK: Pick two points. Rise over run. How far up or down, divided by how far across. And keep the order the same on top and bottom. If you flip it, you get run over rise, which is the other common mistake.
PONO: Remember the clock, too. Math averages about ninety-five seconds a question. Setup in your head, write the numbers, check backward. If the setup isn't there in ten seconds, guess, flag, move.
LEHUA: Recap. Kaden, go.
KADEN: A linear word problem is a starting amount plus a rate. Say the slope in words with units, like negative three gallons per minute, so I don't swap the start and the rate. The trap was calculation slip. I set it up right and then messed up the subtraction. The fix is to check backward, sixteen plus twenty-four is forty. If the choices are numbers, backsolve, start in the middle, and move the right way. If the choices have letters, plug in my own numbers. And for slope off a graph, rise over run, same order.
DEREK: You owned the slip and you fixed it out loud. Eight.
KADEN: I'll take it. I even checked it backward.
LEHUA: Homework. In the app, go to Drill and pick linear functions and graphs. Do ten. On each one, say the slope in words with units before you pick. When you miss one and it says "Trap: calculation slip," redo the arithmetic backward and find the exact step.
PONO: And check one answer on every page by going backward. Make it a habit, not a rescue.
LEHUA: That's episode nine. Next time, episode ten, percent, ratio, and the mean versus the median. I gotta go, it's Wednesday, and the food trucks at the stables run out of the good stuff early.
PONO: Pukalani. Bring me back one plate.
LEHUA: You'll have to fight me for it. Thanks for listening, everybody.
