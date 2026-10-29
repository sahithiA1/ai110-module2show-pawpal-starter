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
The main tradeoff my scheduler makes is choosing simple, readable algorithms over more advanced ones that might give "smarter" results. To build the daily plan, it sorts tasks by priority and then adds them one at a time until the owner runs out of time. This greedy approach puts important tasks first, but it does not always fit the most tasks into the day. For example, in my CLI demo, the scheduler kept the high-priority feeding, walking, and medication tasks but skipped a 45-minute grooming task because no time was left.

I made similar choices for the Phase 4 features:
  - **Sorting:** `sort_by_time()` converts each "HH:MM" time into minutes after midnight and uses Python's `sorted()` with a lambda key. Tasks without a time go at the end. Converting to minutes avoids a bug where comparing strings would put "8:05" after "20:00". One limitation is that it only looks at the clock time, not the date, so it works best for a single day's plan.
  - **Filtering:** `filter_tasks()` uses one list comprehension for the pet name and one for completion status, and skips any filter that is left as `None`. It goes through the full task list every time instead of keeping an index, which is fine for a few pets.
  - **Recurring tasks:** When a daily or weekly task is completed, the scheduler copies it with a new due date using `timedelta`. If the task was overdue, the next one is counted from today so it is not already in the past. Duplicate occurrences are blocked by comparing the pet, title, due date, and time.
  - **Conflict detection:** `detect_conflicts()` compares every pair of timed tasks on the same date and checks whether their time ranges overlap, so it catches both tasks at the exact same time and tasks like a 30-minute walk at 08:00 and a litter box task at 08:15. It returns warning messages instead of raising errors, and it does not move tasks automatically, so the owner decides how to fix the conflict. It also does not check tasks that cross midnight.
- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable because a pet owner usually has only a handful of tasks per day, so performance is not really a concern. Comparing every pair of tasks is technically O(n²), but with ten or twenty tasks it runs instantly, and a more advanced approach like a sweep-line algorithm or an optimization solver would be harder to read, test, and explain. Simple code also made it easier for me to check the AI's work and write tests for each behavior. Putting important care first is also more realistic than squeezing in as many tasks as possible, because missing a medication is worse than missing a bath. The main downside is that the scheduler does not automatically resolve conflicts or find the best possible combination of tasks, but warning the owner and explaining skipped tasks keeps them in control of the final plan.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used Claude Code throughout my PawPal+ project to help with designing, coding, and testing. It helped me create my UML diagram, generate the initial Python class skeletons, and identify improvements to my design. I also used AI to implement the scheduling logic, handle recurring tasks, create a CLI demo, and write automated tests. I reviewed the results and ran the code to make sure everything worked correctly.
- What kinds of prompts or questions were most helpful?
The most helpful prompts were the ones that gave Claude Code specific instructions about what I wanted to accomplish. For example, I asked it to review my UML diagram and class skeletons for missing relationships and scheduling problems. I also asked it to implement the four classes while keeping the existing structure and ensuring the scheduler supported multiple pets. Breaking the project into smaller tasks and asking AI to explain its changes made the development process easier to follow.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment was when Claude Code reviewed my UML diagram and suggested several improvements, including adding extra methods and features. Instead of accepting every suggestion, I focused on the essential changes, such as adding specific task times, due dates, and recurring task support. At that point I chose not to add the optional filter_tasks() method because my early requirements did not need it. In Phase 4, filtering became one of the required features, so I went back and added filter_tasks(), which filters by pet name, completion status, or both. I also used AI suggestions selectively during Phase 4. Before changing any code, I asked Claude Code to review my existing code and explain which features were already done. When it reviewed the finished algorithms, it pointed out a few edge cases. I chose to fix the most important one, which was that an invalid time like "8am" crashed the scheduler, by adding time validation. I left smaller issues, like conflicts that cross midnight, as documented limitations instead of making the code more complicated.
- How did you evaluate or verify what the AI suggested?
I evaluated the AI suggestions by comparing them with my assignment requirements and checking whether they improved the functionality of my project. I worked on one feature at a time and asked Claude Code to explain each change before moving on. After each step, I ran python3 -m pytest -q and python3 main.py to check the results. The CLI demo now shows tasks sorted by time, filtered by pet and completion status, daily and weekly tasks creating their next occurrence, and two conflict warnings. All 30 automated tests pass, which helped me confirm that the AI-generated code worked for the behaviors I tested.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
My tests in tests/test_pawpal.py cover six areas:
  - **Basic tasks:** mark_complete() changes a task's status to completed, and add_task() adds a task to a pet.
  - **Sorting:** sort_by_time() puts tasks added out of order into chronological order, correctly places "8:05" before "20:00", puts tasks without a time at the end, and does not change the original list.
  - **Filtering:** filter_tasks() matches pet names regardless of capitalization, returns only completed or only pending tasks, works with both filters together, returns an empty list for an unknown pet, and returns every task when no filters are given.
  - **Recurring tasks:** Completing a daily task through Scheduler.complete_task() creates a new incomplete task due tomorrow, and a weekly task creates one due seven days later. A non-recurring task does not create anything. I also tested that the new task keeps the same title, pet, priority, duration, and time, that completing the same task twice does not create a duplicate, and that an overdue task's next occurrence is counted from today.
  - **Conflict detection:** I tested two tasks at the exact same time, overlapping tasks for the same pet, and overlapping tasks for different pets. I also tested cases that should not be flagged: the same time on different dates, a task that starts right when another one ends, and a task with no scheduled time.
  - **Time validation:** Valid times like "08:00", "18:30", "8:05", "00:00", and "23:59" are accepted, and an empty time is allowed. Invalid times like "8am", "25:99", "12:60", "24:00", and "hello" raise a ValueError.

I also ran the CLI demo in main.py, which shows all of these features working together on the same sample data.
- Why were these tests important?
These tests were important because recurrence, conflict detection, and time validation all have tricky edge cases that are easy to get wrong. For example, the first version of recurrence gave an overdue task a next due date that was still in the past, and an invalid time like "8am" used to crash the scheduler. Writing tests for these cases helped me make sure the fixes worked and that later changes did not break earlier features. Testing the "should not conflict" cases was just as important as testing real conflicts, because too many false warnings would make the app annoying to use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am fairly confident that my scheduler works correctly for the scenarios I tested. All 30 automated tests pass, and every Phase 4 feature (sorting, filtering, recurring tasks, conflict detection, and time validation) now has its own tests. My CLI demo also builds a schedule for two pets, sorts the tasks by time, filters them, creates the next daily and weekly occurrences, and prints warnings for an exact-time conflict and an overlapping task. My confidence is lower for the Streamlit app, because it is not connected to these features yet.
- What edge cases would you test next if you had more time?
I would test tasks that cross midnight, like a 23:30 task that lasts an hour, because my conflict detection does not catch those yet. I would also test sorting tasks from different dates, since sort_by_time() only looks at the clock time. Other cases I would test are an owner with zero available minutes, several tasks with the same priority, invalid durations like zero or negative minutes, and the full build_daily_plan() result for more than two pets. Once the Streamlit app is connected, I would also test it with invalid user input.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the conflict detection and recurring tasks. My original conflict check only caught tasks that started at exactly the same time, and now it also catches tasks whose durations overlap, like a 30-minute walk at 08:00 and a litter box task at 08:15. The recurring tasks also work through Scheduler.complete_task(), so the next occurrence is created automatically without the user having to add it again. I am also happy that I kept the algorithms short and readable, so I can explain how each one works.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
The biggest thing I would improve is the Streamlit app. Right now app.py lets you add pets and tasks, but it does not have inputs for the scheduled time or recurrence, and the "Generate schedule" button does not call my Scheduler yet. I would connect it so users can see the sorted plan, filters, and conflict warnings in the UI. I would also make sort_by_time() sort by due date and then time, handle tasks that cross midnight, and add tests for the daily plan itself, since my current tests focus on the individual Phase 4 methods. Finally, I would consider a smarter way to fill the day, because the current greedy approach sometimes leaves time unused when a large task does not fit.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned is that AI works best when I break the project into small steps and stay in control of the decisions. Asking Claude Code to review my code before changing anything helped me see which features already existed, and asking it to explain each change helped me understand the code instead of just copying it. I also learned that I still need to check the AI's work myself by running the tests and the demo, because some problems, like the overdue recurrence date and the "8am" crash, only showed up when I tested edge cases.
