# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design for PawPal+ includes four main classes: Owner, Pet, Task, and Scheduler. The diagram shows how these classes connect to manage pet care activities. One owner can have multiple pets, each pet can have multiple tasks, and the scheduler organizes those tasks into a daily plan. I wanted to keep the design simple and organized so it would be easier to implement and maintain.

- What classes did you include, and what responsibilities did you assign to each?
I included four main classes in my PawPal+ design: Owner, Pet, Task, and Scheduler. The Owner class stores the owner's information, available time, preferences, and pets. The Pet class stores details such as the pet's name, species, age, and care tasks. The Task class manages activities like feeding, walking, grooming, and medications, including their duration, priority, and completion status. The Scheduler class is responsible for organizing tasks, checking for scheduling conflicts, and creating a daily plan based on available time and priorities. I separated these responsibilities to keep the system organized and easier to maintain.

**b. Design changes**

- Did your design change during implementation?
Yes, I made a few changes to my initial design after reviewing the UML diagram and Python class skeletons with AI. I kept the same four main classes but added more details to support scheduling conflicts and recurring tasks.
- If yes, describe at least one change and why you made it.
One important change was adding a specific time and due date to the Task class. Initially, tasks only had general preferred times like morning or evening, which made it difficult to identify scheduling conflicts. Adding an exact time allows the scheduler to detect tasks scheduled at the same time, while the due date helps manage recurring tasks. I also added a pet name to each task so the scheduler can identify which pet the activity belongs to. These changes make the design more practical and easier to implement.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considers the owner's available time, task priority, preferred time of day, and preferred task categories. It organizes tasks based on their importance and checks whether each task fits within the owner's available minutes. It also considers due dates and avoids scheduling tasks that have already been completed.
- How did you decide which constraints mattered most?
I decided that task priority and available time were the most important constraints because some pet care activities, such as feeding and medication, are more urgent than others. The scheduler prioritizes high-priority tasks first and then considers the owner's preferences and available time. This helps make sure important pet care activities are included in the daily schedule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff my scheduler makes is prioritizing important tasks over fitting as many tasks as possible into the day. For example, in my CLI demo, the scheduler included feeding, walking, and medication tasks but skipped a 45-minute grooming task because only 35 minutes were left.
- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable because a pet owner may have limited time and needs to complete essential care activities first. Feeding, walking, and medication are generally more important than optional grooming activities. By prioritizing these tasks, the scheduler creates a practical daily plan while explaining which activities could not fit.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude Code throughout my PawPal+ project to help with designing, coding, and testing. It helped me create my UML diagram, generate the initial Python class skeletons, and identify improvements to my design. I also used AI to implement the scheduling logic, handle recurring tasks, create a CLI demo, and write automated tests. I reviewed the results and ran the code to make sure everything worked correctly.
- What kinds of prompts or questions were most helpful?
The most helpful prompts were the ones that gave Claude Code specific instructions about what I wanted to accomplish. For example, I asked it to review my UML diagram and class skeletons for missing relationships and scheduling problems. I also asked it to implement the four classes while keeping the existing structure and ensuring the scheduler supported multiple pets. Breaking the project into smaller tasks and asking AI to explain its changes made the development process easier to follow.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment was when Claude Code reviewed my UML diagram and suggested several improvements, including adding extra methods and features. Instead of accepting every suggestion, I decided to focus only on the essential changes, such as adding specific task times, due dates, and recurring task support. I chose not to add the optional filter_tasks() method because it was not necessary for the main requirements of my assignment. This helped me keep the project simple and manageable.
- How did you evaluate or verify what the AI suggested?
I evaluated the AI suggestions by comparing them with my assignment requirements and checking whether they improved the functionality of my project. After implementing the changes, I ran main.py to verify that the scheduler could organize tasks for multiple pets, respect the owner's available time, and explain skipped tasks. I also ran python -m pytest, and both automated tests passed. This helped me confirm that the AI-generated code worked for the behaviors I tested.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested two main behaviors using pytest. The first test checked whether calling mark_complete() correctly changed a task's completion status from False to True. The second test checked whether adding a task to a Pet increased its task count. I also ran my CLI demo to check that the scheduler could organize tasks for multiple pets, prioritize important activities, and skip tasks that exceeded the owner's available time.
- Why were these tests important?
These tests were important because they helped verify that the basic features of my application worked correctly. Marking tasks as completed helps the system track finished activities, while adding tasks allows pet owners to manage their pets' daily needs. Testing the scheduler through the CLI demo also helped me check that the daily plan was practical and respected time constraints.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am fairly confident that my scheduler works correctly for the basic scenarios I tested. Both automated tests passed, and my CLI demo successfully generated a schedule for two pets while respecting the owner's available time. However, I know that additional testing is needed to confirm that the scheduler handles more complicated situations correctly.
- What edge cases would you test next if you had more time?
If I had more time, I would test situations where multiple tasks overlap, the owner has no available time, or several tasks have the same priority. I would also test recurring tasks across different dates, invalid task durations, and schedules involving more than two pets. These tests would help identify potential problems and make the scheduler more reliable.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
