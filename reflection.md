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
I used Claude Code throughout my PawPal+ project, but in a different way in each phase:
  - **UML design:** It helped me create my UML diagram and reviewed it for missing relationships and scheduling problems. At the end of the project, I had it update the diagram so it matched the final code, including sort_by_time() and filter_tasks().
  - **Python class skeletons:** It turned the UML into class skeletons for Owner, Pet, Task, and Scheduler, and helped me spot improvements to the design, like adding a specific time, due date, and pet name to each task.
  - **Scheduling logic:** It implemented the first version of the scheduler, recurring tasks, and a CLI demo. In Phase 4, I first asked it to only review my code and make a plan. It identified which features already existed, which were partly done, and which were missing. Then I had it add one feature at a time: sorting by time, filtering, the overdue recurrence fix, overlap-based conflict detection, and time validation.
  - **Testing:** It wrote a testing plan that compared my existing tests with what was missing, and pointed out that build_daily_plan() had no tests at all. It wrote the new tests and helped me check whether they were meaningful.
  - **Streamlit integration:** My earlier commit only connected adding pets and tasks; the Generate schedule button was still a placeholder. In the final phase, Claude Code planned the integration in small steps, and then built them one at a time: schedule generation, task inputs for time and recurrence, conflict warnings, sorting and filtering, and marking tasks complete. After each step it checked the app with Streamlit's AppTest tool.
  - **Documentation:** It helped me update the README and this reflection after each phase so they matched what the code actually did.
- What kinds of prompts or questions were most helpful?
The most helpful prompts were the ones that gave Claude Code specific instructions about what I wanted to accomplish. For example, I asked it to review my UML diagram and class skeletons for missing relationships and scheduling problems. I also asked it to implement the four classes while keeping the existing structure and ensuring the scheduler supported multiple pets. Breaking the project into smaller tasks and asking AI to explain its changes made the development process easier to follow.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment was when Claude Code reviewed my UML diagram and suggested several improvements, including adding extra methods and features. Instead of accepting every suggestion, I focused on the essential changes, such as adding specific task times, due dates, and recurring task support. At that point I chose not to add the optional filter_tasks() method because my early requirements did not need it. In Phase 4, filtering became one of the required features, so I went back and added filter_tasks(), which filters by pet name, completion status, or both. I also used AI suggestions selectively during Phase 4. Before changing any code, I asked Claude Code to review my existing code and explain which features were already done. When it reviewed the finished algorithms, it pointed out a few edge cases. I chose to fix the most important one, which was that an invalid time like "8am" crashed the scheduler, by adding time validation. I left smaller issues, like conflicts that cross midnight, as documented limitations instead of making the code more complicated.

I also changed AI-generated work in the testing phase. One of the new daily plan tests, the priority test, passed even when priority was ignored completely. Instead of keeping it as written, I had it reordered so it actually fails when the scheduler ignores priority.
- How did you evaluate or verify what the AI suggested?
I treated myself as the lead architect of the project and Claude Code as the assistant doing most of the typing. I made the design decisions and controlled the scope of each step. Many of my prompts asked for a review or a plan only, with no file changes, so I could decide what to do before any code was written. I limited which files could be changed in each step, and I decided which suggestions to accept, change, or skip. For example, I chose to count overdue recurring tasks forward from today, and I chose to shorten my local folder path in the README's test output for privacy.

I worked on one feature at a time and asked Claude Code to explain each change before moving on. After each step, I made sure python3 -m pytest was run and checked the results, and during the backend phases I also ran python3 main.py to see the CLI demo. For the Streamlit app, each step was checked with Streamlit's AppTest tool, which clicks through the app without a browser and reports what appears on the page. Nothing was committed until I approved it, and I chose the commit messages myself.

This process caught a real bug. While testing Mark Complete in the UI, the test showed that the success message appeared but the original task stayed pending. The cause was that Scheduler.complete_task() checked whether a task was in the pet's list by comparing field values, so a copied task with the same fields was accepted and marked complete instead of the real one. The UI was changed to always pass the real task, and then I had the backend fixed so complete_task() only accepts the pet's actual task object, with a regression test that failed on the old code and passes on the new code. All 38 automated tests now pass.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I have 38 automated tests in tests/test_pawpal.py, and they cover seven areas:
  - **Basic tasks:** mark_complete() changes a task's status to completed, and add_task() adds a task to a pet.
  - **Sorting:** sort_by_time() puts tasks added out of order into chronological order, correctly places "8:05" before "20:00", puts tasks without a time at the end, and does not change the original list.
  - **Filtering:** filter_tasks() matches pet names regardless of capitalization, returns only completed or only pending tasks, works with both filters together, returns an empty list for an unknown pet, and returns every task when no filters are given.
  - **Recurring tasks:** Completing a daily task through Scheduler.complete_task() creates a new incomplete task due tomorrow, and a weekly task creates one due seven days later. A non-recurring task does not create anything. I also tested that the new task keeps the same title, pet, priority, duration, and time, that completing the same task twice does not create a duplicate, and that an overdue task's next occurrence is counted from today. A regression test also checks that passing a copy of a task to complete_task() raises a ValueError and does not change the original task or create a new occurrence.
  - **Conflict detection:** I tested two tasks at the exact same time, overlapping tasks for the same pet, and overlapping tasks for different pets. I also tested cases that should not be flagged: the same time on different dates, a task that starts right when another one ends, and a task with no scheduled time.
  - **Time validation:** Valid times like "08:00", "18:30", "8:05", "00:00", and "23:59" are accepted, and an empty time is allowed. Invalid times like "8am", "25:99", "12:60", "24:00", and "hello" raise a ValueError.
  - **Daily plan:** In the Testing and Verification phase, I added seven tests for build_daily_plan(), which had no tests before. They check that the plan never goes over the owner's available minutes and keeps high-priority tasks over low-priority ones, that a task that does not fit is skipped while smaller tasks are still scheduled, that tasks exactly filling the available time are all scheduled, and that an owner with zero minutes gets an empty plan. They also check that an owner with no pets or a pet with no tasks gets an empty plan without errors, that overdue tasks are included while completed and future tasks are left out, and that the chosen tasks are listed in time order even though they are picked by priority.

I also ran the CLI demo in main.py, which shows all of these features working together on the same sample data. For the Streamlit app, each integration step was checked with Streamlit's AppTest tool: adding timed and untimed tasks, generating a schedule, exact-time and overlapping conflict warnings, the pet and status filters, sorting with untimed tasks last, and completing one-time, daily, and weekly tasks without creating duplicates. These AppTest checks were run during development but are not saved in the repository as automated tests.

I also tested the app myself in my browser with Streamlit. I added Mochi as a pet and created a 30-minute, high-priority Morning Walk task at 08:00 that repeats daily. I generated the daily schedule and confirmed the walk appeared correctly. Then I marked Morning Walk complete and checked that the original task showed as Completed and the next day's occurrence showed as Pending.

AI also helped me check whether my tests were actually useful. Claude Code ran my new daily plan tests against deliberately broken versions of the scheduler, changed only in memory, to see if the tests would catch the mistakes. Most bugs were caught, but a version that ignored priority completely still passed my priority test. The problem was that the low-priority Bath task was too long to fit anyway, so it was skipped for the wrong reason. I fixed the test by adding the Bath task first, so a scheduler that ignored priority would pick it and fail the test. After that change, every broken version made at least one test fail. This taught me that a passing test does not always prove what its name says.
- Why were these tests important?
These tests were important because recurrence, conflict detection, time validation, and the daily plan all have tricky edge cases that are easy to get wrong. For example, the first version of recurrence gave an overdue task a next due date that was still in the past, and an invalid time like "8am" used to crash the scheduler. Writing tests for these cases helped me make sure the fixes worked and that later changes did not break earlier features. Testing the "should not conflict" cases was just as important as testing real conflicts, because too many false warnings would make the app annoying to use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am confident that my scheduler works correctly for the scenarios I tested, and I would rate it 4 out of 5 stars. All 38 automated tests pass. Every scheduling feature (sorting, filtering, recurring tasks, conflict detection, and time validation) has its own tests, and the daily plan is tested for priorities, time limits, and empty task lists. The Streamlit app is now fully connected to the backend: it can generate the schedule, show conflict warnings, sort and filter tasks, and complete daily and weekly tasks, and each of those steps was checked with AppTest. My CLI demo also shows the same features working together.

I am not giving it 5 stars for a few reasons. The app's AppTest checks are not saved as automated tests, so a future change to app.py could break something without a test failing. There are also known limitations: conflicts that cross midnight are not detected, sort_by_time() ignores the due date, and all data is lost when the page is refreshed.
- What edge cases would you test next if you had more time?
I would test tasks that cross midnight, like a 23:30 task that lasts an hour, because my conflict detection does not catch those yet. I would also test sorting tasks from different dates, since sort_by_time() only looks at the clock time. Other cases I would test are several tasks with the same priority, invalid durations like zero or negative minutes, and a daily plan for more than two pets. For the app, I would turn the AppTest checks into saved tests, especially for completing recurring tasks and making sure reruns do not create duplicates.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the conflict detection and recurring tasks. My original conflict check only caught tasks that started at exactly the same time, and now it also catches tasks whose durations overlap, like a 30-minute walk at 08:00 and a litter box task at 08:15. The recurring tasks also work through Scheduler.complete_task(), so the next occurrence is created automatically without the user having to add it again. I am also happy that I kept the algorithms short and readable, so I can explain how each one works.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would focus on making the app more practical to use every day:
  - **Persistent storage:** Right now pets and tasks only live in Streamlit's session state, so refreshing the page loses everything. I would save them to a file, like JSON, or a small database so they are still there the next day.
  - **Editing and deleting:** The app can add and complete tasks, but it cannot edit or delete them. The backend already has remove_pet() and remove_task(), so I would connect those and add a way to edit a task's details.
  - **Saved UI tests:** I would turn the AppTest checks I ran during development into automated tests in the repository, so the app is tested every time I run pytest, not just the backend.
  - **Smaller improvements:** Letting the owner set preferred categories in the app, showing the reason each task was scheduled, making sort_by_time() sort by due date and then time, and handling tasks that cross midnight.

Finally, I would consider a smarter way to fill the day, because the current greedy approach sometimes leaves time unused when a large task does not fit.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
One important thing I learned is that AI works best when I break the project into small steps and stay in control of the decisions. Asking Claude Code to review my code before changing anything helped me see which features already existed, and asking it to explain each change helped me understand the code instead of just copying it. I also learned that I still need to check the AI's work myself by running the tests and the demo, because some problems, like the overdue recurrence date and the "8am" crash, only showed up when I tested edge cases.
