@ -0,0 +1,145 @@



EVERYONE should read this one before starting. This file denotes how the instructions for each of your divisions are structured.

But more importantly, **this file will have all of the protocols you need to follow when contributing to this project**.

If you know how to use git, and are confident with using the python libraries in requirements.txt,
    you should be fine with just skim reading this.

# -------------- Before you Start ---------------

If you don't know how to use python and have never touched a programming language before, go learn that first.


# ----------- Main Objective ---------------

You are tasked to create an entire pipeline for SotonLM's data engineering as a whole.
The flow of the pipeline should be as follows : 
    Data Fetching -> Raw Data Storage -> Cleaning -> Cleaning Evaluation -> Clean Data Storage

Each section of the flow will be detailed in the instructions.md file given for each division's directory.


# -------------- Things you NEED to Know about the Stack ------------------

This entire section will run you through everything we're using to build the data engineering pipeline.


## --------- Version Control -----------
This project is in a git repository, and therefore is version controlled.

If you don't know how to use git, here's a short rundown of what you need to know about version control:

### Making changes to the project
Let's say your genius mind changed a few things in the project...

This could be implementing a new function, changing an existing implementation, fixing bugs, etc.

To update the main project, you will have to push these changes into the main repository.
In other words, other contributors will get your changes and be able to work on top of them.

below will be some terminal commands for you to do this, so make sure git is installed in your system.


### git add .
this stages all the files you changed to commit. 
If you want to commit specific files, change the . into the filename of the one you want to add.

### git commit -m {MESSAGE}
Locally commits all the added changes to the repository.
**WARNING**: this doesn't mean that everyone can see your changes just yet.


Its like locally adding a version to the project. 
Any changes you make to the repository after the commit means that 
    you are working on a newer version on top of your last commit.

You would also want to replace the MESSAGE with a meaningful report that summarises what you changed.

### The Mahoraga method
When you are writing a message for commits, there's actually a rule on how a message should start.
Why? Probably cuz its neat but idk.

Examples of messages would be:
'Add profile picture UI component to settings page'
'Resolve login page crash on mobile Safari'

Yes these examples are AI generated but you should get the idea.
Notice that the messages aren't in past tense. This clarifies that your commit is an attempt of whatever 
    fixes you made, or whatever new implementation, and not an absolute solution.

If that's not explanation wasn't clear, use the Mahoraga template:

'With this commit, I will... {Message}'
    example: (with this commit, I will) 'Resolve login page crash on mobile Safari'
        exclude all in the brackets.

(And yes, I named this template based on one of the lines from jjk.)

### git push {branch}
This command publishes all of the commits you made onto the repository.

A branch refers to an alternate bunch of updates independent to the main development.

Typically, there's the main branch which holds all the functionalities which are verified to work,
    and all of the WIP functionalities have their own branches so that they can be in development
    without disturbing the main branch.

The main branch is the product of the project. **DO NOT DIRECTLY PUSH CHANGES ONTO THE MAIN BRANCH**.

You would want to create a branch for every time you plan a semi-major implementation/bugfix:

```
    git checkout -b your-branch-name #creates branch and moves you to the branch
    git checkout your-branch-name #moves you to that branch, in case you were working on another one.
    
    #make sure to keep the branch updated to the current version of main

    git merge main
```
Lets go back to the command in subject.

Once you use git push, all commits you made will be onto the public version of the repository, 
    and people can work on top of them.
Note that using git push without specifying the branch just means that commits will be pushed 
    onto the current branch that you are in.

## -----To make things easier-----

If you dont like the terminal or just want version control to be simpler, use the github desktop app.

For most of the time, it will make things so much easier.



## --------- Python Libraries ----------

The libraries required for development are all in requirements.txt.
You can install all libraries in it with this magical command:
```
    pip install -r requirements.txt
```
Make sure to install the requirements txt libraries for your division as well.

Requirements txt ensures that all contributors are on the same page with the libraries 
    that should be used to work on this project.
However, don't let that stop you from using another library to develop things - just make sure to
    add the new library used into the requirements txt file.

If you want to learn what each library does, I recommend a mix of asking AI and reading documentations.

    (Small rant - I kinda hate how counterintuitive solutions to things became after AI chatbots came to be.
    But alas, "asking AI" is the best answer to most things...)






# ----- If you made it this far... ------
After understanding how to contribute to this project, you should go and get the gist of 
    **what to contribute to this project**.

Start off by going to your division's directory and going through its instructions.md.