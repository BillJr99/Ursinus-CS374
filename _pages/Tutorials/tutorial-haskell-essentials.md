---
layout: notes
permalink: /Tutorials/HaskellEssentials
title: "CS374: Haskell Essentials for the Programming Languages Course"

info:
  coursenum: CS374
  goals:
    - "Written and run basic Haskell expressions in GHCi, using `:t` to inspect types and `:l` to load files"
    - "Defined pure functions using pattern matching, guards, and list comprehensions"
    - "Implemented common higher-order functions (`map`, `filter`, `foldr`) and understood their types in the Hindley-Milner type system"
    - "Connected Haskell's lazy evaluation to the normal-order reduction strategy from the lambda calculus module"
    - "Read and modified a TidalCycles pattern to understand how Haskell's design choices show up in live-coding music code"

tags:
  - haskell
  - functional

---
# Tutorial: Haskell Essentials for the Programming Languages Course

## Learning Goals

By the end of this tutorial, you will have:

- Written and run basic Haskell expressions in GHCi, using `:t` to inspect types and `:l` to load files
- Defined pure functions using pattern matching, guards, and list comprehensions
- Implemented common higher-order functions (`map`, `filter`, `foldr`) and understood their types in the Hindley-Milner type system
- Connected Haskell's lazy evaluation to the normal-order reduction strategy from the lambda calculus module
- Read and modified a TidalCycles pattern to understand how Haskell's design choices show up in live-coding music code

Haskell is the host language for TidalCycles, the live-coding music system we have been using throughout this course.  It is also the language that most clearly embodies the lambda calculus: every Haskell function is a lambda term, the type system is Hindley-Milner, and lazy evaluation is the normal-order reduction strategy made practical.  This tutorial gives you enough Haskell to read TidalCycles code, write simple Haskell programs, and understand why Haskell's design choices feel the way they do after our theory modules.

**What you need:**
- GHCi, the Haskell interactive environment: `sudo apt install ghc` or `brew install ghc`
- Alternatively, use [Replit](https://replit.com/languages/haskell) or [Try Haskell](https://www.tryhaskell.org/) online

---

# Part 1: The Basics

## 1.1 GHCi First Steps

```haskell
-- Start GHCi: type ghci at your terminal
-- Every line is an expression; GHCi evaluates and prints it.

Prelude> 3 + 4
7

Prelude> "hello" ++ " " ++ "world"
"hello world"

Prelude> 2 ^ 10
1024

Prelude> True && False
False

Prelude> not True
False
```

**`:t` shows the type of any expression:**

```haskell
Prelude> :t 42
42 :: Num p => p

Prelude> :t "hello"
"hello" :: [Char]

Prelude> :t (+)
(+) :: Num a => a -> a -> a

Prelude> :t True
True :: Bool
```

---

## 1.2 Functions

In Haskell, functions are defined at the top level with pattern matching.  Every function is curried by default.

```haskell
-- functions.hs
double :: Int -> Int
double x = x * 2

add :: Int -> Int -> Int
add x y = x + y

-- Partial application: fix the first argument
add5 :: Int -> Int
add5 = add 5       -- add5 is add with first arg fixed to 5

-- Anonymous function (lambda)
square :: Int -> Int
square = \x -> x * x
```

Load in GHCi:

```haskell
Prelude> :l functions.hs
Prelude> double 7          -- 14
Prelude> add 3 4           -- 7
Prelude> add5 10           -- 15
Prelude> square 9          -- 81
```

**Key insight:** `add :: Int -> Int -> Int` is actually `add :: Int -> (Int -> Int)`: a function that takes an Int and returns a function.  Application is left-associative: `add 3 4` means `(add 3) 4`.

---

## 1.3 Lists

Haskell's list is a singly-linked list (like Scheme's). `[1, 2, 3]` is sugar for `1 : 2 : 3 : []`.

```haskell
-- Basic list operations
Prelude> head [1,2,3]           -- 1 (first element)
Prelude> tail [1,2,3]           -- [2,3] (everything but first)
Prelude> [1,2,3] ++ [4,5]       -- [1,2,3,4,5] (concatenation)
Prelude> length [1,2,3]         -- 3
Prelude> reverse [1,2,3]        -- [3,2,1]
Prelude> take 3 [1..10]         -- [1,2,3]
Prelude> drop 3 [1..10]         -- [4,5,6,7,8,9,10]
Prelude> zip [1,2,3] ["a","b","c"]   -- [(1,"a"),(2,"b"),(3,"c")]

-- List ranges
Prelude> [1..5]           -- [1,2,3,4,5]
Prelude> [1,3..10]        -- [1,3,5,7,9]  (step 2)
Prelude> [10,9..1]        -- [10,9,8,...,1]

-- Infinite lists (safe because Haskell is lazy)
Prelude> take 5 [1..]     -- [1,2,3,4,5]
Prelude> take 5 (repeat 0)  -- [0,0,0,0,0]
Prelude> take 8 (cycle [1,2,3])  -- [1,2,3,1,2,3,1,2]
```

---

## 1.4 Pattern Matching

Pattern matching is the idiomatic way to define recursive functions in Haskell:

```haskell
-- List operations by pattern matching

myLength :: [a] -> Int
myLength []     = 0
myLength (_:xs) = 1 + myLength xs

mySum :: Num a => [a] -> a
mySum []     = 0
mySum (x:xs) = x + mySum xs

myMap :: (a -> b) -> [a] -> [b]
myMap _ []     = []
myMap f (x:xs) = f x : myMap f xs

myFilter :: (a -> Bool) -> [a] -> [a]
myFilter _ []     = []
myFilter p (x:xs)
    | p x       = x : myFilter p xs
    | otherwise =     myFilter p xs

-- Test in GHCi:
-- myLength [1,2,3,4,5]  => 5
-- mySum [1..10]          => 55
-- myMap (*2) [1..5]      => [2,4,6,8,10]
-- myFilter even [1..10]  => [2,4,6,8,10]
```

**Guards** (`| condition = expression`) are the idiomatic Haskell replacement for if-else chains, especially when multiple conditions are needed.

---

# Part 2: Higher-Order Functions

## 2.1 map, filter, foldl, foldr

```haskell
-- The big four of Haskell:
Prelude> map (*2) [1..5]               -- [2,4,6,8,10]
Prelude> filter even [1..10]           -- [2,4,6,8,10]
Prelude> foldl (+) 0 [1..10]           -- 55 (left fold, like reduce)
Prelude> foldr (:) [] [1,2,3]          -- [1,2,3] (right fold; (:) is cons)

-- foldl vs foldr: same result for +, different for non-associative ops
Prelude> foldl  (-) 0 [1,2,3]          -- ((0-1)-2)-3 = -6
Prelude> foldr  (-) 0 [1,2,3]          -- 1-(2-(3-0)) = 2

-- Haskell's foldr is lazy: it can process infinite lists with some functions
Prelude> foldr (\x acc -> if x > 5 then acc else x:acc) [] [1..]
-- This terminates! foldr is lazy in the accumulator.
-- Result: [1,2,3,4,5]
```

---

## 2.2 Function Composition and Application

Haskell has two essential operators that correspond to the birds:

- `(.)` is the **Bluebird**: `(f . g) x = f (g x)`
- `($)` is the **Thrush**: `f $ x = f x` (low-precedence application, avoids parentheses)

```haskell
Prelude> ((*2) . (+1)) 3           -- (*2)((+1)(3)) = 8
Prelude> map ((*2) . (+1)) [1..5]  -- [4,6,8,10,12]

-- Without $:
Prelude> negate (abs (negate (-3)))
-- With $:
Prelude> negate $ abs $ negate (-3)

-- Pointfree pipeline using (.) and ($):
process :: [Int] -> Int
process = sum . filter even . map (*2)
-- process [1..5] = sum(filter even(map(*2)[1..5]))
--                = sum(filter even[2,4,6,8,10])
--                = sum[2,4,6,8,10] = 30
```

---

## 2.3 Lambda and Sections

```haskell
-- Lambda (anonymous function):
Prelude> (\x -> x * x) 5           -- 25

-- Operator section: partially apply an operator
Prelude> (*2) 5                     -- 10  (right section)
Prelude> (2*) 5                     -- 10  (left section - same for *)
Prelude> (2-) 5                     -- -3  (left section)
Prelude> subtract 2 5               -- 3   (use subtract for right section of -)
Prelude> map (*3) [1..5]            -- [3,6,9,12,15]
Prelude> filter (>3) [1..6]         -- [4,5,6]
```

---

# Part 3: Types in Depth

## 3.1 Type Classes

A **type class** defines a set of operations that a type must support.  It is Haskell's mechanism for **ad-hoc polymorphism** (like interfaces in Java, but more powerful):

```haskell
-- Num: types that support arithmetic
Prelude> :info Num
class Num a where
  (+) :: a -> a -> a
  (-) :: a -> a -> a
  (*) :: a -> a -> a
  ...

-- Eq: types that support equality
Prelude> :info Eq
class Eq a where
  (==) :: a -> a -> Bool
  (/=) :: a -> a -> Bool

-- Show: types that can be converted to String
Prelude> show 42       -- "42"
Prelude> show True     -- "True"
Prelude> show [1,2,3]  -- "[1,2,3]"

-- Ord: types with an ordering (extends Eq)
Prelude> compare 3 5   -- LT
Prelude> max 3 5       -- 5
```

The constraint `Num a =>` in a type signature means "this works for any type `a` that is an instance of `Num`."

---

## 3.2 Algebraic Data Types

Haskell's data types are **algebraic**, built from sums (OR) and products (AND):

```haskell
-- A sum type: a Shape is EITHER a Circle OR a Rectangle
data Shape = Circle Double
           | Rectangle Double Double
           deriving (Show)

-- A product type: a Point has BOTH an x AND a y
data Point = Point Double Double
           deriving (Show)

-- Pattern match on constructors:
area :: Shape -> Double
area (Circle r)      = pi * r * r
area (Rectangle w h) = w * h

-- The Maybe type: EITHER Nothing OR Just a value
data Maybe a = Nothing | Just a

safeDiv :: Int -> Int -> Maybe Int
safeDiv _ 0 = Nothing
safeDiv x y = Just (x `div` y)

-- Either: Left for error, Right for success (convention)
safeHead :: [a] -> Either String a
safeHead []    = Left "empty list"
safeHead (x:_) = Right x
```

---

## 3.3 Record Syntax

```haskell
-- Record syntax: named fields
data Person = Person
    { firstName :: String
    , lastName  :: String
    , age       :: Int
    } deriving (Show)

-- Construction:
alice = Person { firstName = "Alice", lastName = "Smith", age = 30 }

-- Access by field name:
Prelude> firstName alice    -- "Alice"
Prelude> age alice          -- 30

-- Update (creates a new value; nothing is mutated):
older_alice = alice { age = 31 }
```

---

# Part 4: Haskell and TidalCycles

## 4.1 Reading Tidal Code

TidalCycles is a library of Haskell types and functions.  A Tidal pattern like:

```haskell
d1 $ sound "bd sn [cp cp] hh"
```

desugars as:
- `d1 :: ControlPattern -> IO ()`: sends a pattern to audio channel 1
- `($) :: (a -> b) -> a -> b`: applies `sound ...` to `d1`
- `sound :: String -> ControlPattern`: creates a pattern from a sample name string
- `"bd sn [cp cp] hh"`: the mini-notation string (parsed by a Tidal parser)

A more complex Tidal expression:

```haskell
d1 $ every 4 (fast 2) $ sound "bd sn"
```

- `every :: Int -> (Pattern a -> Pattern a) -> Pattern a -> Pattern a`
- `fast :: Rational -> Pattern a -> Pattern a`
- `every 4 (fast 2)` is a partial application: `every` needs 3 args, given 2, returns a `Pattern a -> Pattern a` function
- `($)` applies that function to `sound "bd sn"`

This is all lambda calculus! `every 4 (fast 2)` is $\lambda p.\ \texttt{every}\ 4\ (\texttt{fast}\ 2)\ p$ with the final parameter implicit.

---

## 4.2 Writing Your First Haskell Functions for Tidal

```haskell
-- pattern-utils.hs - utilities to use in TidalCycles

-- A function that alternates between two patterns every n cycles:
alternate :: Int -> a -> a -> [a]
alternate n a b = concat (replicate n [a, b])
-- alternate 2 "bd" "sn" = ["bd","bd","sn","sn","bd","bd","sn","sn"]

-- A function that interleavse two lists:
interleave :: [a] -> [a] -> [a]
interleave []     ys     = ys
interleave xs     []     = xs
interleave (x:xs) (y:ys) = x : y : interleave xs ys
-- interleave [1,2,3] [10,20,30] = [1,10,2,20,3,30]

-- Map a transformation over every nth element:
everyNth :: Int -> (a -> a) -> [a] -> [a]
everyNth n f xs = zipWith apply [0..] xs
  where apply i x = if i `mod` n == 0 then f x else x

-- Generate a Euclidean rhythm as a list of Booleans
-- euclidean k n: k beats distributed as evenly as possible over n steps
euclidean :: Int -> Int -> [Bool]
euclidean k n = go k (n - k) (replicate k [True]) (replicate (n-k) [False])
  where
    go 0 _  acc _       = concat acc
    go _ _  acc []      = concat acc
    go k' r' acc extras
        | k' <= r'  = go (min k' (length extras)) (r' - k') (zipWith (++) acc extras) (drop k' extras)
        | otherwise = go (r' `mod` k') (k' - r') acc extras
```

---

# Part 5: Practical Exercises

## 5.1 Exercises

1.  **Rewrite in Haskell.**  Translate the following Python into idiomatic Haskell:
   - `[x**2 for x in range(1, 11)]`: list comprehension of squares
   - `list(filter(lambda x: x % 2 == 0, range(1, 21)))`: even numbers
   - `from functools import reduce; reduce(lambda a, b: a * b, range(1, 6))`: factorial via reduce

2.  **Pattern match a tree.**  Define a Haskell data type `Tree a = Leaf | Node a (Tree a) (Tree a)`.  Implement: `depth :: Tree a -> Int`, `size :: Tree a -> Int`, `toList :: Tree a -> [a]` (in-order traversal).  Test in GHCi.

3.  **Church numerals in Haskell.**  Define the Church numerals `zero`, `one`, `two`, `three` as Haskell functions (type: `(a -> a) -> a -> a`).  Define `succC`, `addC`, `mulC`.  Write `toInt :: ((Int -> Int) -> Int -> Int) -> Int` and verify `toInt (addC two three) == 5`.

4.  **Infinite lists.**  Write `fibs :: [Integer]` as an infinite list using `zipWith (+) fibs (tail fibs)`.  Take the first 20.  Write `primes :: [Int]` using the Sieve of Eratosthenes: `primes = sieve [2..]` where `sieve (p:xs) = p : sieve [x | x <- xs, x `mod` p /= 0]`.  Take the first 15 primes.

5.  **TidalCycles reading.**  In GHCi with TidalCycles loaded, type `:t every`, `:t fast`, `:t slow`, `:t stack`, `:t cat`.  For each type signature, write a one-sentence English explanation of what the function does, and give one concrete usage example with the expected behavior.

---

## Further Reading

- Hutton, Graham.  *Programming in Haskell* (2nd ed., Cambridge UP, 2016).  The clearest introduction; Chapters 1-8 are essential.
- Lipovaca, Miran.  *Learn You a Haskell for Great Good!*  Free online.  Friendlier but thorough.
- McLean, Alex.  *TidalCycles* source code and documentation.  Reading real Haskell library code is the best advanced exercise.
- Bird, Richard.  *Thinking Functionally with Haskell* (Cambridge UP, 2014).  Beautiful algebraic reasoning about programs; connects to the formal methods in this course.
