"""
Seed data for BrainFeed — 61 questions across 6 subjects.
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.models import Question


QUESTIONS = [
    # === APTITUDE ===
    {"subject": "Aptitude", "topic": "Number Series", "subtopic": "Pattern Recognition", "exam_tag": "GATE,CAT", "difficulty": "Medium", "question_text": "What comes next in the sequence: 2, 6, 12, 20, 30, ... ?", "options": '["38","42","46","52"]', "correct_answer": "42", "explanation": "Differences: 4,6,8,10,12. Next = 30+12 = 42."},
    {"subject": "Aptitude", "topic": "Percentages", "subtopic": "Basic Percentage", "exam_tag": "CAT,JEE", "difficulty": "Easy", "question_text": "If 40% of a number is 200, what is the number?", "options": '["400","500","600","800"]', "correct_answer": "500", "explanation": "200/0.4 = 500"},
    {"subject": "Aptitude", "topic": "Profit & Loss", "subtopic": "Basic P&L", "exam_tag": "CAT", "difficulty": "Medium", "question_text": "A shopkeeper buys an item for ₹800 and sells it for ₹960. What is the profit percentage?", "options": '["15%","20%","25%","16%"]', "correct_answer": "20%", "explanation": "Profit = 160, Profit% = 160/800 × 100 = 20%"},
    {"subject": "Aptitude", "topic": "Time & Work", "subtopic": "Combined Work", "exam_tag": "GATE,CAT", "difficulty": "Hard", "question_text": "A can do a work in 10 days, B in 15 days. Together they work for 4 days. What fraction of the work is left?", "options": '["1/3","2/3","1/6","5/6"]', "correct_answer": "1/3", "explanation": "Combined rate = 1/10+1/15 = 1/6. In 4 days = 4/6 = 2/3 done. Left = 1/3."},
    {"subject": "Aptitude", "topic": "Speed & Distance", "subtopic": "Relative Speed", "exam_tag": "CAT", "difficulty": "Medium", "question_text": "A train 150m long passes a pole in 15 seconds. What is the speed of the train in km/h?", "options": '["36","40","10","45"]', "correct_answer": "36", "explanation": "Speed = 150/15 = 10 m/s = 36 km/h"},
    {"subject": "Aptitude", "topic": "Averages", "subtopic": "Weighted Average", "exam_tag": "CAT,GATE", "difficulty": "Easy", "question_text": "The average of 5 numbers is 20. If one number is excluded, the average becomes 18. What is the excluded number?", "options": '["28","30","24","26"]', "correct_answer": "28", "explanation": "Total = 100, remaining = 72, excluded = 28."},
    {"subject": "Aptitude", "topic": "Ratio & Proportion", "subtopic": "Basic Ratio", "exam_tag": "CAT", "difficulty": "Easy", "question_text": "If A:B = 3:4 and B:C = 5:6, then A:B:C is?", "options": '["15:20:24","3:4:6","9:12:16","5:6:8"]', "correct_answer": "15:20:24", "explanation": "Make B common: A:B = 15:20, B:C = 20:24, so A:B:C = 15:20:24."},
    {"subject": "Aptitude", "topic": "Simple Interest", "subtopic": "SI Formula", "exam_tag": "CAT,JEE", "difficulty": "Easy", "question_text": "Find simple interest on ₹5000 at 10% for 3 years.", "options": '["₹1500","₹1000","₹1200","₹500"]', "correct_answer": "₹1500", "explanation": "SI = PNR/100 = 5000×3×10/100 = 1500."},
    # === REASONING ===
    {"subject": "Reasoning", "topic": "Blood Relations", "subtopic": "Family Tree", "exam_tag": "GATE,UPSC", "difficulty": "Hard", "question_text": "If A is the brother of B; B is the sister of C; and C is the father of D, how is D related to A?", "options": '["Brother","Nephew/Niece","Uncle","Cousin"]', "correct_answer": "Nephew/Niece", "explanation": "A and C are siblings. D is child of C, so D is nephew/niece of A."},
    {"subject": "Reasoning", "topic": "Coding-Decoding", "subtopic": "Letter Shift", "exam_tag": "GATE,CAT", "difficulty": "Medium", "question_text": "If COMPUTER is coded as DPNQVUFS, how is MOBILE coded?", "options": '["NPCJMF","NPCKNG","NPCJMG","LNAHKD"]', "correct_answer": "NPCJMF", "explanation": "Each letter is shifted by +1 in the alphabet."},
    {"subject": "Reasoning", "topic": "Syllogisms", "subtopic": "Logical Deduction", "exam_tag": "GATE,UPSC", "difficulty": "Medium", "question_text": "All cats are animals. Some animals are dogs. Which conclusion follows?", "options": '["All dogs are cats","Some cats are dogs","Some animals are cats","No cat is a dog"]', "correct_answer": "Some animals are cats", "explanation": 'From "All cats are animals" → some animals are cats (conversion).'},
    {"subject": "Reasoning", "topic": "Logical Puzzles", "subtopic": "Seating Arrangement", "exam_tag": "CAT,GATE", "difficulty": "Hard", "question_text": "5 people sit in a row. A sits at one end. B is next to A. C is not next to B. D is between C and E. Who sits in the middle?", "options": '["A","B","D","C"]', "correct_answer": "D", "explanation": "Arrangement: A-B-E-D-C or A-B-D-E-C. D sits in or near middle."},
    {"subject": "Reasoning", "topic": "Analogies", "subtopic": "Word Analogy", "exam_tag": "GATE,UPSC", "difficulty": "Easy", "question_text": "Book is to Reading as Fork is to ___?", "options": '["Writing","Eating","Cooking","Drawing"]', "correct_answer": "Eating", "explanation": "A book is used for reading; a fork is used for eating."},
    {"subject": "Reasoning", "topic": "Direction Sense", "subtopic": "Navigation", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "A man walks 5km North, turns right and walks 3km, turns right again and walks 5km. Which direction is he facing?", "options": '["North","South","East","West"]', "correct_answer": "South", "explanation": "North → Right(East) → Right(South). Facing South."},
    {"subject": "Reasoning", "topic": "Number Series", "subtopic": "Pattern", "exam_tag": "GATE,CAT", "difficulty": "Medium", "question_text": "Find the missing number: 3, 9, 27, 81, ___?", "options": '["162","243","192","324"]', "correct_answer": "243", "explanation": "Geometric progression ×3: 81×3 = 243."},
    # === CODING ===
    {"subject": "Coding", "topic": "Data Structures", "subtopic": "Arrays", "exam_tag": "GATE,JEE", "difficulty": "Easy", "question_text": "What is the time complexity of accessing an element in an array by index?", "options": '["O(1)","O(n)","O(log n)","O(n²)"]', "correct_answer": "O(1)", "explanation": "Direct index access is constant time O(1)."},
    {"subject": "Coding", "topic": "Algorithms", "subtopic": "Sorting", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "What is the worst-case time complexity of Quick Sort?", "options": '["O(n log n)","O(n²)","O(n)","O(log n)"]', "correct_answer": "O(n²)", "explanation": "When pivot selection is poor (already sorted), Quick Sort degrades to O(n²)."},
    {"subject": "Coding", "topic": "Programming", "subtopic": "Frameworks", "exam_tag": "GATE,JEE", "difficulty": "Medium", "question_text": "Which of the following is NOT a JavaScript framework?", "options": '["React","Django","Vue","Angular"]', "correct_answer": "Django", "explanation": "Django is a Python web framework, not JavaScript."},
    {"subject": "Coding", "topic": "Data Structures", "subtopic": "Linked Lists", "exam_tag": "GATE", "difficulty": "Hard", "question_text": "What is the time complexity of inserting at the beginning of a singly linked list?", "options": '["O(1)","O(n)","O(log n)","O(n²)"]', "correct_answer": "O(1)", "explanation": "Just update the head pointer — constant time."},
    {"subject": "Coding", "topic": "Algorithms", "subtopic": "Searching", "exam_tag": "GATE,JEE", "difficulty": "Easy", "question_text": "Binary Search works on which type of data?", "options": '["Sorted","Unsorted","Random","Linked List"]', "correct_answer": "Sorted", "explanation": "Binary Search requires sorted data to work correctly."},
    {"subject": "Coding", "topic": "Programming", "subtopic": "OOP", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "Which OOP principle allows a child class to provide a specific implementation of a parent method?", "options": '["Encapsulation","Polymorphism","Abstraction","Inheritance"]', "correct_answer": "Polymorphism", "explanation": "Method overriding is a form of polymorphism."},
    {"subject": "Coding", "topic": "Database", "subtopic": "SQL", "exam_tag": "GATE", "difficulty": "Easy", "question_text": "Which SQL command is used to retrieve data from a database?", "options": '["INSERT","UPDATE","SELECT","DELETE"]', "correct_answer": "SELECT", "explanation": "SELECT is the DQL command for retrieving data."},
    {"subject": "Coding", "topic": "Algorithms", "subtopic": "Graph", "exam_tag": "GATE", "difficulty": "Hard", "question_text": "What is the time complexity of Dijkstra's algorithm with a binary heap?", "options": '["O(V²)","O((V+E) log V)","O(V log V)","O(E²)"]', "correct_answer": "O((V+E) log V)", "explanation": "With a binary heap priority queue, Dijkstra runs in O((V+E) log V)."},
    # === MATHS ===
    {"subject": "Maths", "topic": "Linear Algebra", "subtopic": "Matrices", "exam_tag": "GATE,JEE", "difficulty": "Hard", "question_text": "What is the determinant of the identity matrix of order 3?", "options": '["0","1","3","Undefined"]', "correct_answer": "1", "explanation": "The determinant of any identity matrix is always 1."},
    {"subject": "Maths", "topic": "Calculus", "subtopic": "Differentiation", "exam_tag": "GATE,JEE", "difficulty": "Medium", "question_text": "What is the derivative of x³ with respect to x?", "options": '["x²","3x²","3x","x³"]', "correct_answer": "3x²", "explanation": "d/dx(xⁿ) = nxⁿ⁻¹, so d/dx(x³) = 3x²."},
    {"subject": "Maths", "topic": "Probability", "subtopic": "Basic Probability", "exam_tag": "GATE,JEE,CAT", "difficulty": "Easy", "question_text": "What is the probability of getting a head when flipping a fair coin?", "options": '["1/4","1/2","1/3","1"]', "correct_answer": "1/2", "explanation": "Fair coin has 2 outcomes, P(Head) = 1/2."},
    {"subject": "Maths", "topic": "Set Theory", "subtopic": "Set Operations", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "If A = {1,2,3} and B = {2,3,4}, what is A ∩ B?", "options": '["{1,2,3,4}","{2,3}","{1,4}","{1}"]', "correct_answer": "{2,3}", "explanation": "Intersection contains common elements: {2,3}."},
    {"subject": "Maths", "topic": "Number Theory", "subtopic": "Primes", "exam_tag": "GATE,JEE", "difficulty": "Easy", "question_text": "Which of the following is a prime number?", "options": '["91","87","67","51"]', "correct_answer": "67", "explanation": "67 has no divisors other than 1 and itself."},
    {"subject": "Maths", "topic": "Calculus", "subtopic": "Integration", "exam_tag": "GATE,JEE", "difficulty": "Hard", "question_text": "What is ∫(1/x) dx?", "options": '["x²","ln|x| + C","1/x² + C","e^x + C"]', "correct_answer": "ln|x| + C", "explanation": "The integral of 1/x is the natural logarithm ln|x| + C."},
    # === VERBAL ===
    {"subject": "Verbal", "topic": "Vocabulary", "subtopic": "Synonyms", "exam_tag": "CAT,UPSC", "difficulty": "Easy", "question_text": 'Choose the synonym of "Ephemeral":', "options": '["Permanent","Transient","Solid","Lengthy"]', "correct_answer": "Transient", "explanation": "Ephemeral means short-lived or transient."},
    {"subject": "Verbal", "topic": "Grammar", "subtopic": "Tenses", "exam_tag": "CAT,UPSC", "difficulty": "Medium", "question_text": "Choose the correct sentence:", "options": '["He has went home","He has gone home","He have gone home","He has go home"]', "correct_answer": "He has gone home", "explanation": "Present perfect: has + past participle (gone)."},
    {"subject": "Verbal", "topic": "Reading Comprehension", "subtopic": "Inference", "exam_tag": "CAT,UPSC", "difficulty": "Hard", "question_text": '"The market showed resilience despite global headwinds." What does this imply?', "options": '["Market crashed","Market remained stable","Market grew rapidly","Market was closed"]', "correct_answer": "Market remained stable", "explanation": "Resilience despite headwinds implies stability under pressure."},
    {"subject": "Verbal", "topic": "Vocabulary", "subtopic": "Antonyms", "exam_tag": "CAT,UPSC", "difficulty": "Easy", "question_text": 'Choose the antonym of "Benevolent":', "options": '["Kind","Malevolent","Generous","Caring"]', "correct_answer": "Malevolent", "explanation": "Benevolent (kind) is opposite of Malevolent (wishing harm)."},
    {"subject": "Verbal", "topic": "Sentence Completion", "subtopic": "Fill in the blank", "exam_tag": "CAT", "difficulty": "Medium", "question_text": "The scientist's theory was so ___ that even experts struggled to comprehend it.", "options": '["Simple","Abstruse","Common","Clear"]', "correct_answer": "Abstruse", "explanation": "Abstruse means difficult to understand, fitting the context."},
    # === CORE SUBJECTS ===
    {"subject": "Core Subjects", "topic": "Digital Logic", "subtopic": "Logic Gates", "exam_tag": "GATE", "difficulty": "Easy", "question_text": "What is the output of an AND gate when both inputs are 1?", "options": '["0","1","Undefined","X"]', "correct_answer": "1", "explanation": "AND gate outputs 1 only when all inputs are 1."},
    {"subject": "Core Subjects", "topic": "Computer Networks", "subtopic": "OSI Model", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "How many layers are in the OSI model?", "options": '["5","6","7","4"]', "correct_answer": "7", "explanation": "OSI model has 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application."},
    {"subject": "Core Subjects", "topic": "Operating Systems", "subtopic": "Process Scheduling", "exam_tag": "GATE", "difficulty": "Hard", "question_text": "Which scheduling algorithm can cause starvation?", "options": '["Round Robin","FCFS","Shortest Job First","All of the above"]', "correct_answer": "Shortest Job First", "explanation": "SJF can starve long jobs if short jobs keep arriving."},
    {"subject": "Core Subjects", "topic": "DBMS", "subtopic": "Normalization", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "Which normal form eliminates transitive dependencies?", "options": '["1NF","2NF","3NF","BCNF"]', "correct_answer": "3NF", "explanation": "3NF removes transitive dependencies from non-prime attributes."},
    {"subject": "Core Subjects", "topic": "Digital Logic", "subtopic": "Boolean Algebra", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "What is the simplified form of A + AB?", "options": '["A","B","AB","A+B"]', "correct_answer": "A", "explanation": "A + AB = A(1+B) = A·1 = A (Absorption law)."},
    {"subject": "Core Subjects", "topic": "Computer Architecture", "subtopic": "Memory", "exam_tag": "GATE", "difficulty": "Medium", "question_text": "Which memory is the fastest?", "options": '["RAM","Cache","Hard Disk","Register"]', "correct_answer": "Register", "explanation": "Registers are the fastest memory, located inside the CPU."},
    {"subject": "Core Subjects", "topic": "Theory of Computation", "subtopic": "Automata", "exam_tag": "GATE", "difficulty": "Hard", "question_text": "Which type of automaton recognizes context-free languages?", "options": '["Finite Automaton","Pushdown Automaton","Turing Machine","Linear Bounded Automaton"]', "correct_answer": "Pushdown Automaton", "explanation": "PDAs with a stack can recognize context-free grammars."},
    {"subject": "Core Subjects", "topic": "Compiler Design", "subtopic": "Parsing", "exam_tag": "GATE", "difficulty": "Hard", "question_text": "Which parsing technique uses a stack and is bottom-up?", "options": '["Recursive Descent","LL(1)","LR Parsing","Predictive Parsing"]', "correct_answer": "LR Parsing", "explanation": "LR parsing is a bottom-up technique using a stack and parse table."},
    # === MORE APTITUDE ===
    {"subject": "Aptitude", "topic": "Compound Interest", "subtopic": "CI Formula", "exam_tag": "CAT,JEE", "difficulty": "Hard", "question_text": "What is the compound interest on ₹10000 at 10% per annum for 2 years?", "options": '["₹2000","₹2100","₹2200","₹1900"]', "correct_answer": "₹2100", "explanation": "A = P(1+r/100)^n = 10000(1.1)² = 12100. CI = 2100."},
    {"subject": "Aptitude", "topic": "Permutations", "subtopic": "Arrangements", "exam_tag": "GATE,JEE", "difficulty": "Medium", "question_text": "In how many ways can 4 people be seated in a row?", "options": '["12","24","16","48"]', "correct_answer": "24", "explanation": "4! = 4×3×2×1 = 24."},
    {"subject": "Aptitude", "topic": "Probability", "subtopic": "Dice", "exam_tag": "GATE,CAT", "difficulty": "Medium", "question_text": "What is the probability of getting a sum of 7 when rolling two dice?", "options": '["1/6","5/36","1/12","7/36"]', "correct_answer": "1/6", "explanation": "6 favorable outcomes out of 36: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1). P = 6/36 = 1/6."},
    {"subject": "Aptitude", "topic": "Mixtures", "subtopic": "Alligation", "exam_tag": "CAT", "difficulty": "Hard", "question_text": "Two solutions of 30% and 50% concentrations are mixed to get 40%. In what ratio?", "options": '["1:1","2:3","3:2","1:2"]', "correct_answer": "1:1", "explanation": "Alligation: (50-40):(40-30) = 10:10 = 1:1."},
    {"subject": "Aptitude", "topic": "Geometry", "subtopic": "Triangles", "exam_tag": "JEE,GATE", "difficulty": "Medium", "question_text": "What is the area of a triangle with base 10 cm and height 6 cm?", "options": '["60 cm²","30 cm²","20 cm²","15 cm²"]', "correct_answer": "30 cm²", "explanation": "Area = ½ × base × height = ½ × 10 × 6 = 30 cm²."},
]


def seed(db: Session):
    """Seed questions if the database is empty."""
    count = db.query(Question).count()
    if count > 0:
        print(f"[Seed] Database already has {count} questions. Skipping seed.")
        return

    for q_data in QUESTIONS:
        question = Question(
            id=str(uuid.uuid4()),
            subject=q_data["subject"],
            topic=q_data["topic"],
            subtopic=q_data["subtopic"],
            exam_tag=q_data["exam_tag"],
            difficulty=q_data["difficulty"],
            question_text=q_data["question_text"],
            options=q_data["options"],
            correct_answer=q_data["correct_answer"],
            explanation=q_data["explanation"],
        )
        db.add(question)

    db.commit()
    print(f"[Seed] Inserted {len(QUESTIONS)} questions.")
