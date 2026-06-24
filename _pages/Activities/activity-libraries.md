---
layout: activity
permalink: /Activities/Libraries
title: "CS374: Programming Language Principles - Static and Dynamic Linked Libraries"


info: 
  goals: 
    - To describe the linker process
    - To differentiate between static and dynamic libraries, particularly with respect to their advantages and disadvantages
  models:
    - model: |
        <img src="../images/activity-libraries/Libraries.png" alt="A flowchart indicating the linking process of several code modules with static libraries into a unified executable file, which may then load dynamic symbols via shared libraries at runtime.">
      title: Libraries
      questions:
        - "Where is the code for each static library stored for execution?  What are the advantages and disadvantages of this choice?"
        - "Where is the code for each dynamic linked library stored for execution?  What are the advantages and disadvantages of this choice?"   
        
tags:
  - libraries
  - linker
  
---


## Example Library

<iframe height="500px" width="100%" src="https://www.billmongan.com/Ursinus-CS374/assets/code-viewer.html?zip=https%3A%2F%2Fraw.githubusercontent.com%2FBillJr99%2FUrsinus-CS374%2Fgh-pages%2Ffiles%2Freplit%2FDynamicMallocLibrary.zip&title=Dynamic%20System%20Library%20Example" scrolling="yes" frameborder="no" allowfullscreen="true" sandbox="allow-scripts allow-same-origin"></iframe>
