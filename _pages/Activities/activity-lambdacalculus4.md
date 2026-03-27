---
layout: activity
permalink: /Activities/LambdaCalculus4
title: "CS374: Programming Language Principles - The Lambda Calculus"


info: 
  prev: ./LambdaCalculus2
  goals: 
    - To explore examples of Church Encodings and mathematics in the Lambda Calculus using the Scheme and node.js languages
        
tags:
  - lambdacalculus
  
---

Recursion with the Y-Combinator

Y = λf.(λx.f(x x))(λx.f(x x))      <--- what combinator(s) do you see here?  Why might this be problematic?

Y g = (λf.(λx.f(x x))(λx.f(x x))) g

Y g = (λx.g (x x)) (λx.g (x x)) : after b-reduction of g for f

Y g = g ((λx.g (x x)) (λx.g (x x))) : after b-reduction of right parameter into left function for x

Y g = g (Y g) : substitution of Y = lambda f.(lambda x.f(x x))(λx.f(x x)) in inner parameter

 

*From <https://en.wikipedia.org/wiki/Fixed-point_combinator#Fixed-point_combinators_in_lambda_calculus>*

 

(define ycombinator ((lambda (f) (lambda (x) (f (x x)))) (lambda (x) (f (x x)))))

 

Y = f =&gt; x =&gt; f(f(x)(x))(f(x)(x))

console.log(Y('g'))

Z = λg.(λx.g(λv.xxv))(λx.g(λv.xxv))            <--- how might this help solve the issue above?

const Z = g => (x => g(v => x(x)(v)))(x => g(v => x(x)(v)))

From https://medium.com/swlh/y-and-z-combinators-in-javascript-lambda-calculus-with-real-code-31f25be934ec


Church Numerals:

(define n0 (lambda (f a) a))

(define n1 (lambda (f a) (f a)))

(define n2 (lambda (f a) (f (f a))))

const jsnum = n =&gt; n(x =&gt; x + 1)(0);

 

n0 = f =&gt; a =&gt; a

n1 = f =&gt; a =&gt; f(a)

n2 = f =&gt; a =&gt; f(f(a))

n3 = f =&gt; a =&gt; f(f(f(a)))

n4 = f =&gt; a =&gt; f(f(f(f(a))))

 

console.log(jsnum(n4))

**What is the pattern?**

 

The Church numeral **n** is the application of a function **f**, **n** times, to a variable **a**.

(f….f a)

 

Suppose you wanted to define a function that accepts a Church numeral n, like n2, and add 1 to it. What would you do? Hint: Recall that **n** is a function on **f** and **a** that is already a certain number of applications of **f**!

 

(define succ (lambda (n f a) (\_\_\_\_ (n f a))))

 

 

Mathematics on Church Numerals in Scheme:

 

Add together **n** and **k** by applying **succ** to **k**, **n** times

(define add (lambda (n k) (succ n k)))

 

(define mult (lambda (n k f) (n (k f)))) ; n times, apply k times to f

> ; This is the Bluebird Combinator
>
>  

(define bluebird (lambda (f g a) (f (g a)))) ; composition

(define mult (lambda (n k f) (bluebird n k f)))

 

 

(define pow (lambda (n k) (k n)))

 

(define cardinal (lambda (f a b) (f b a))) ; Flip parameters - there are 3

> ; parameters, how can we
>
> ; "eliminate" one?

(define thrush (lambda (a f) (f a))) ; (cardinal identity)

(define pow (lambda (n k) (thrush n k)))

 

And in node.js:

 

succ = n =&gt; f =&gt; a =&gt; f(n(f)(a))

 

console.log(jsnum(succ(n0)))

 

B = f =&gt; g =&gt; a =&gt; f(g(a))

 

succB = n =&gt; f =&gt; B(f)(n(f))

console.log(jsnum(succB(n1)))

 

add = n =&gt; k =&gt; n(succ)(k)

 

console.log(jsnum(add(n2)(n3)))

 

mult = n =&gt; k =&gt; f =&gt; n(k(f))

multB = n =&gt; k =&gt; f =&gt; B(n)(k)(f)

 

console.log(jsnum(mult(n2)(n3)))

console.log(jsnum(multB(n2)(n3)))

 

pow = n =&gt; k =&gt; k(n)

 

console.log(jsnum(pow(n3)(n2)))

 

 

 

Via Lambda Calculus Reductions:

 

succ(n) = λwyx.y(wyx) (n)

succ(0) = λwyx.y(wyx) (0)

= λwyx.y(wyx) (λnz.z)

= λnz.n(z) = 1

 

mult(x, y) = λxyz.x(yz)

mult(3, 2) = λxyz.x(yz) 3 2 ; 3 f's and 2 f's

= λz.3(2z) = 6 ; apply the 3 f's to a 2 times

; by substituting 2z for each of the 3 f's

 
*From <https://math.stackexchange.com/questions/595518/how-to-multiply-in-lambda-calculus>*

 

A Lambda Calculus Program:

 

// <https://glebec.github.io/lambda-talk/>

fib = n =&gt; n(f =&gt; a =&gt; b =&gt; f(b)(add(a)(b)))(T)(n0)(n1)

console.log(jsnum(fib(n4)))

 

(define fib (lambda (n) (n ((lambda (f a b) (f (b (add a b))) (kite 0 1))))))

 

 

Factorial?

 

; n containing a function f will invoke krestel false,

; otherwise if n is a with no f calls, it will select true

(define is0 (lambda (n) (n (krestel false) true)))

 

; <https://courses.cs.washington.edu/courses/cse341/03au/slides/Lambda/tsld015.htm>

(define factorial ((lambda (x) (lambda (y) x (y y)) (lambda (y) x (y y)))     &lt;--- y combinator!
(lambda (f) (lambda (n) (is0 n) 1 (mult n (f (pred n)))))))

 

Can you reduce all the function calls to their lambda states for substitution?
 
// <https://gist.github.com/TeWu/96cc5a49fce3fa0c6defcf5c50bdf309>

// Sources / See also:

// Church encoding @ Wikipedia: <https://en.wikipedia.org/wiki/Church_encoding>

// Programming with Nothing by Tom Stuart: <https://youtu.be/VUhlNx_-wYk>

// Y Not- Adventures in Functional Programming by Jim Weirich: <https://youtu.be/FITJMJjASUs>

// https://medium.com/swlh/y-and-z-combinators-in-javascript-lambda-calculus-with-real-code-31f25be934ec
