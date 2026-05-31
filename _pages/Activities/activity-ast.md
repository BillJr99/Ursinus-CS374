---
layout: activity
permalink: /Activities/AST
title: "CS374: Programming Language Principles - Abstract Syntax Trees"


info: 
  goals: 
    - To define an Abstract Syntax Tree for a given grammar
    - To augment grammars with attribute grammars
  models:
    - model: |
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
         /* From https://en.wikipedia.org/wiki/Attribute_grammar */
         Expr → Expr + Term
         Expr → Term
         Term → Term * Factor
         Term → Factor
         Factor → "(" Expr ")"
         Factor → integer
        ]]></script>
        <br>
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
         /* From https://en.wikipedia.org/wiki/Attribute_grammar */
         /* S-Attributed Grammar: Synthesized Values, but no Inherited Attributes (from neighboring nonterminals in the production) */
         Expr1 → Expr2 + Term [ Expr1.value = Expr2.value + Term.value ]
         Expr → Term [ Expr.value = Term.value ]
         Term1 → Term2 * Factor [ Term1.value = Term2.value * Factor.value ]
         Term → Factor [ Term.value = Factor.value ]
         Factor → "(" Expr ")" [ Factor.value =  Expr.value ]
         Factor → integer [ Factor.value = strToInt(integer.str) ]
        ]]></script>
      title: Attribute Grammars
      questions:
        - "Where do you think inherited attributes might come from?"
        - "What are some other attributes you might associate with productions?"
        - "Suppose an Expression is the product of a Term and a Factor.  How might you determine the type (<code>float</code> or <code>int</code>) of the resulting Expression?"
    - model: |
        <a title="Dcoetzee, CC0, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Abstract_syntax_tree_for_Euclidean_algorithm.svg"><img width="512" alt="Abstract syntax tree for Euclidean algorithm" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Abstract_syntax_tree_for_Euclidean_algorithm.svg"></a>
        <br>
        <script type="syntaxhighlighter" class="brush: cpp"><![CDATA[
        /* From https://en.wikipedia.org/wiki/Abstract_syntax_tree */
        euclidean_gcd(a, b):
            while b ≠ 0
              if a > b
                a := a − b
              else
                b := b − a
            return a
        ]]></script>
      title: "Abstract Syntax Trees (AST)"
      questions:
        - "In what ways is this simpler than a full parse tree?  What items are retained, and which are omitted?"
        
tags:
  - ast
  
---

