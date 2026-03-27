---
layout: activity
permalink: /Activities/LambdaCalculus3
title: "CS374: Programming Language Principles - The Lambda Calculus"


info: 
  prev: ./LambdaCalculus2
  next: ./LambdaCalculus4
  goals: 
    - To explore examples of combinators in the Lambda Calculus using the Scheme and node.js languages
        
tags:
  - lambdacalculus
  
---

**Primitive Functions**:

λx.x

 

**Beta Reduction**:

(λx.x) y = y ; substutution

 

**Alpha Reduction**: Renaming parameters

 

**"Bird" Combinators**:

(λx.x) - Identity (I)

> In node.js:  
> I = a =&gt; a
>
> console.log(I(1))  
>  
>
> In Scheme:  
> (define identity (lambda (x) x))  
> (display (identity 10)) (newline)
>
>  

(λf.(f f)) - Mockingbird (M)

> In node.js:  
> M = f =&gt; f(f)
>
> console.log(M(I))  
> // console.log(M(M)) // ???  
>  
>
> In Scheme:  
> (define mockingbird (lambda (f) (f f)))
>
>  

(λa λb.a) also written via **Currying** as (λab.a) - Krestel (K) == True

 

> In node.js:  
> K = a =&gt; b =&gt; a  
> console.log(K(1)(2))  
>   
> In Scheme:  
> (define krestel (lambda (a b) a))  
> (display (krestel 1 2)) (newline)  
>  

 

What is K(I)(1)(2)?  
((λab.a) I 1) 2

I 2

(λx.x) 2

2

 

K(I) = (λab.b): the Kite (False)

 

In node.js:

console.log(K(I)(1)(2))

KI = a =&gt; b =&gt; b

 

In Scheme:

(define kestrel (lambda (a b) a)) ; const, true

(display (kestrel 1 2)) (newline)

(define kite (lambda (a b) (kestrel identity a) b))

 

In node.js:

 

const T = K

const F = KI

 

Not Operator:

(λx.x\_\_ \_\_)

When x is true, select false, and when x is false, select true.

Remember that true chooses the first of two options, and false selects the second. Arrange these so that true selects false, and false selects true!

 

not = p =&gt; p(\_\_\_)(\_\_\_)

console.log(not(T))

console.log(not(F))

 

In scheme:

(define not2 (lambda (p) (p \_\_\_\_ \_\_\_\_)))

(display ((not2 true) 1 2)) (newline)

<table>
<colgroup>
<col style="width: 54%" />
<col style="width: 45%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>P</strong></th>
<th><strong>not P</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>T</td>
<td>F</td>
</tr>
<tr class="even">
<td>F</td>
<td>T</td>
</tr>
</tbody>
</table>

 

And Operator:

(λpq.p\_\_ \_\_)

When p is false, what must the result of the AND operator be? Where should that result go (recall that true selects the first option, and false selects the second option!).

When p is true, the AND might be true or false - which variable do we need to check?

 

and2 = p =&gt; q =&gt; p(\_\_)(\_\_)

 

console.log(and2(T)(T))

console.log(and2(F)(T))

 

In Scheme:

(define and2 (lambda (p q) (p \_\_ \_\_)))

<table>
<colgroup>
<col style="width: 35%" />
<col style="width: 35%" />
<col style="width: 29%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>P</strong></th>
<th><strong>Q</strong></th>
<th><strong>P and Q</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>F</td>
<td>F</td>
<td>F</td>
</tr>
<tr class="even">
<td>F</td>
<td>T</td>
<td>F</td>
</tr>
<tr class="odd">
<td>T</td>
<td>F</td>
<td>F</td>
</tr>
<tr class="even">
<td>T</td>
<td>T</td>
<td>T</td>
</tr>
</tbody>
</table>

 

Or Operator:

(λpq.p\_\_ \_\_)

When p is true, what must the result of the OR operator be? Where should that result go?

When p is false, the OR might be true or false - which variable do we need to check?

 

or2 = p =&gt; q =&gt; p(\_\_)(\_\_)

 

console.log(or2(T)(T))

console.log(or2(F)(T))

 

In Scheme:

(define or2 (lambda (p q) (p \_\_ \_\_)))

 

Alternative: or3 = p =&gt; q =&gt; M(p)(q) // ppq, because M(p) = pp

 
<table>
<colgroup>
<col style="width: 35%" />
<col style="width: 35%" />
<col style="width: 29%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>P</strong></th>
<th><strong>Q</strong></th>
<th><strong>P or Q</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>F</td>
<td>F</td>
<td>F</td>
</tr>
<tr class="even">
<td>F</td>
<td>T</td>
<td>T</td>
</tr>
<tr class="odd">
<td>T</td>
<td>F</td>
<td>T</td>
</tr>
<tr class="even">
<td>T</td>
<td>T</td>
<td>T</td>
</tr>
</tbody>
</table>

XOR Operator:

When x is true, the XOR is only true if y is false, and false otherwise: in other words, the XOR is the opposite of y

When x is false, the XOR is only true if y is true, and false if y is false (y)

 

How does this relate to equality?

 

not (x xor y)

(λxy.\_\_\_\_\_\_\_\_\_\_\_\_)

(λxy.(x (not y) y) false true)

(λxy.(x (y false true) y) false true)

Alternatively, the opposite of xor:
(λxy.(x y (not y)))



<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 26%" />
<col style="width: 21%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>P</strong></th>
<th><strong>Q</strong></th>
<th><strong>P xor Q</strong></th>
<th><strong>P == Q</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>F</td>
<td>F</td>
<td>F</td>
<td>T</td>
</tr>
<tr class="even">
<td>F</td>
<td>T</td>
<td>T</td>
<td>F</td>
</tr>
<tr class="odd">
<td>T</td>
<td>F</td>
<td>T</td>
<td>F</td>
</tr>
<tr class="even">
<td>T</td>
<td>T</td>
<td>F</td>
<td>T</td>
</tr>
</tbody>
</table>


