; Recursion, closures, and functions as values.
(define fact (lambda (n) (if (= n 0) 1 (* n (fact (- n 1))))))
(fact 5)
(define adder (lambda (a) (lambda (b) (+ a b))))
(define add3 (adder 3))
(add3 4)
(define map1 (lambda (f xs)
  (if (null? xs) (quote ()) (cons (f (car xs)) (map1 f (cdr xs))))))
(map1 add3 (quote (1 2 3)))
