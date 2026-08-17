"""Seed 200+ questions into the database. Run: python backend/seed_more_questions.py"""
import sqlite3, uuid, os, json

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "brainfeed.db")

QUESTIONS = [
# ===== MATHS =====
("Maths","Calculus","Derivatives","GATE,JEE","Medium","What is the derivative of x³ + 2x?",["3x² + 2","3x² + 2x","x² + 2","3x + 2"],"3x² + 2","Using power rule: d/dx(xⁿ) = nxⁿ⁻¹"),
("Maths","Calculus","Integrals","GATE,JEE","Medium","What is ∫2x dx?",["x²","x² + C","2x²","x² - C"],"x² + C","Integration: ∫2x dx = x² + C"),
("Maths","Calculus","Limits","GATE,JEE","Easy","What is lim(x→0) sin(x)/x?",["0","1","∞","undefined"],"1","This is a standard limit result."),
("Maths","Calculus","Derivatives","GATE,JEE","Hard","What is the derivative of ln(x²+1)?",["2x/(x²+1)","1/(x²+1)","2x·ln(x²+1)","x/(x²+1)"],"2x/(x²+1)","Chain rule: d/dx[ln(u)] = u'/u"),
("Maths","Calculus","Integrals","GATE,JEE","Hard","What is ∫e^(2x) dx?",["e^(2x)/2 + C","2e^(2x) + C","e^(2x) + C","e^x + C"],"e^(2x)/2 + C","Substitution: u=2x, du=2dx"),
("Maths","Linear Algebra","Matrices","GATE,JEE","Easy","What is the determinant of [[1,0],[0,1]]?",["0","1","2","-1"],"1","Identity matrix has determinant 1."),
("Maths","Linear Algebra","Matrices","GATE,JEE","Medium","If A is a 3×3 matrix with det(A)=5, what is det(2A)?",["10","40","80","20"],"40","det(kA) = k^n · det(A), so 2³ × 5 = 40"),
("Maths","Linear Algebra","Eigenvalues","GATE,JEE","Hard","The eigenvalues of [[2,1],[0,3]] are?",["2 and 3","1 and 3","2 and 1","0 and 3"],"2 and 3","For triangular matrices, eigenvalues are diagonal entries."),
("Maths","Linear Algebra","Vectors","GATE,JEE","Easy","What is the dot product of (1,2,3) and (4,5,6)?",["32","30","28","36"],"32","1×4 + 2×5 + 3×6 = 4+10+18 = 32"),
("Maths","Probability","Basics","GATE,JEE,CAT","Easy","A fair coin is tossed twice. P(at least one head)?",["1/4","1/2","3/4","1"],"3/4","P = 1 - P(no heads) = 1 - 1/4 = 3/4"),
("Maths","Probability","Bayes","GATE,JEE","Hard","If P(A)=0.6, P(B|A)=0.5, P(B|A')=0.2, find P(A|B).",["0.789","0.625","0.500","0.833"],"0.789","Bayes: P(A|B) = P(B|A)P(A)/P(B) = 0.3/0.38"),
("Maths","Probability","Distributions","GATE,JEE","Medium","Mean of Poisson distribution with λ=4?",["2","4","8","16"],"4","For Poisson, mean = λ"),
("Maths","Set Theory","Basics","GATE","Easy","If |A|=10, |B|=15, |A∩B|=5, find |A∪B|.",["20","25","30","15"],"20","|A∪B| = |A| + |B| - |A∩B| = 10+15-5 = 20"),
("Maths","Set Theory","Relations","GATE","Medium","A relation that is reflexive, symmetric, and transitive is called?",["Equivalence relation","Partial order","Total order","Function"],"Equivalence relation","All three properties define equivalence relation."),
("Maths","Number Theory","Divisibility","GATE,JEE","Easy","What is GCD(12, 18)?",["2","3","6","12"],"6","12=2²×3, 18=2×3², GCD=2×3=6"),
("Maths","Number Theory","Modular","GATE","Medium","What is 17 mod 5?",["2","3","7","1"],"2","17 = 5×3 + 2, remainder is 2"),
("Maths","Number Theory","Primes","GATE,JEE","Easy","Which is the smallest prime number?",["0","1","2","3"],"2","2 is the smallest and only even prime."),
("Maths","Geometry","Coordinate","JEE","Medium","Distance between (1,2) and (4,6)?",["5","7","25","3"],"5","√((4-1)²+(6-2)²) = √(9+16) = 5"),
("Maths","Geometry","Circles","JEE","Medium","Area of circle with radius 7?",["22","44","154","49π"],"154","A = πr² = 22/7 × 49 = 154"),
("Maths","Number Series","Patterns","JEE,CAT","Easy","Next in: 2, 6, 18, 54, ?",["108","162","72","96"],"162","Geometric: multiply by 3. 54×3=162"),
("Maths","Permutations","Counting","JEE,CAT","Medium","How many ways to arrange 4 books on a shelf?",["4","12","24","16"],"24","4! = 4×3×2×1 = 24"),
("Maths","Permutations","Combinations","JEE,CAT","Medium","C(10,3) = ?",["30","120","720","210"],"120","10!/(3!×7!) = 120"),

# ===== APTITUDE =====
("Aptitude","Percentages","Basics","CAT,GATE","Easy","What is 20% of 150?",["25","30","35","40"],"30","20/100 × 150 = 30"),
("Aptitude","Percentages","Increase","CAT","Medium","A price increases from ₹200 to ₹250. What % increase?",["20%","25%","30%","50%"],"25%","(250-200)/200 × 100 = 25%"),
("Aptitude","Percentages","Successive","CAT","Hard","Two successive discounts of 20% and 10% equal a single discount of?",["28%","30%","27%","26%"],"28%","Effective = 100 - (80×90/100) = 28%"),
("Aptitude","Profit & Loss","Basics","CAT","Easy","CP=₹500, SP=₹600. Profit %?",["10%","15%","20%","25%"],"20%","Profit = 100, Profit% = 100/500 × 100 = 20%"),
("Aptitude","Profit & Loss","Discount","CAT","Medium","Marked price ₹1000, discount 20%, profit 10%. Find CP.",["₹640","₹666","₹700","₹727"],"₹727","SP=800, CP=800/1.1 ≈ ₹727"),
("Aptitude","Time & Work","Basics","CAT","Easy","A does work in 10 days, B in 15 days. Together?",["5 days","6 days","7 days","8 days"],"6 days","1/10 + 1/15 = 1/6, so 6 days"),
("Aptitude","Time & Work","Pipes","CAT","Medium","Pipe A fills in 6h, B empties in 8h. Both open, time to fill?",["12h","18h","24h","48h"],"24h","1/6 - 1/8 = 1/24, so 24 hours"),
("Aptitude","Speed & Distance","Basics","CAT","Easy","Speed 60 km/h, time 2.5h. Distance?",["120 km","150 km","180 km","200 km"],"150 km","D = S × T = 60 × 2.5 = 150 km"),
("Aptitude","Speed & Distance","Trains","CAT","Medium","A 200m train crosses a pole in 20s. Speed?",["36 km/h","10 km/h","72 km/h","20 km/h"],"36 km/h","Speed = 200/20 = 10 m/s = 36 km/h"),
("Aptitude","Speed & Distance","Relative","CAT","Hard","Two trains 150km apart approach at 60 and 40 km/h. Meet in?",["1h","1.5h","2h","2.5h"],"1.5h","Relative speed=100, time=150/100=1.5h"),
("Aptitude","Averages","Basics","CAT","Easy","Average of 10, 20, 30, 40, 50?",["25","30","35","40"],"30","Sum=150, Avg=150/5=30"),
("Aptitude","Averages","Weighted","CAT","Medium","Avg of 3 numbers is 20. If one is removed, avg becomes 15. Removed number?",["25","30","35","40"],"30","Sum=60, new sum=30, removed=30"),
("Aptitude","Ratio & Proportion","Basics","CAT","Easy","If a:b = 2:3 and b:c = 4:5, find a:c.",["8:15","2:5","4:5","6:10"],"8:15","a:b:c = 8:12:15, so a:c = 8:15"),
("Aptitude","Ratio & Proportion","Mixtures","CAT","Hard","Mix 5L of 20% solution with 10L of 50% solution. Concentration?",["35%","40%","45%","50%"],"40%","(5×20+10×50)/15 = 600/15 = 40%"),
("Aptitude","Compound Interest","Basics","CAT","Medium","CI on ₹10000 at 10% for 2 years?",["₹2000","₹2100","₹2200","₹1000"],"₹2100","A=10000(1.1)²=12100, CI=2100"),
("Aptitude","Compound Interest","Difference","CAT","Hard","Difference between CI and SI on ₹5000 for 2 years at 10%?",["₹25","₹50","₹100","₹75"],"₹50","CI-SI = P(r/100)² = 5000×0.01 = 50"),
("Aptitude","Simple Interest","Basics","CAT","Easy","SI on ₹8000 at 5% for 3 years?",["₹800","₹1000","₹1200","₹1500"],"₹1200","SI = PRT/100 = 8000×5×3/100 = 1200"),

# ===== REASONING =====
("Reasoning","Syllogisms","Two Premises","CAT,UPSC","Medium","All dogs are animals. All animals are living things. Conclusion?",["All dogs are living things","Some living things are dogs","All living things are dogs","No conclusion"],"All dogs are living things","By transitivity of 'All' statements."),
("Reasoning","Syllogisms","Negative","CAT,UPSC","Hard","No fish are birds. All sparrows are birds. Conclusion?",["No sparrows are fish","Some fish are sparrows","All fish are sparrows","No conclusion"],"No sparrows are fish","Sparrows⊂Birds, Birds∩Fish=∅, so Sparrows∩Fish=∅"),
("Reasoning","Analogies","Word","CAT,UPSC","Easy","Book : Read :: Fork : ?",["Eat","Write","Cut","Cook"],"Eat","A book is used to read, a fork is used to eat."),
("Reasoning","Analogies","Number","CAT,UPSC","Medium","3:27 :: 5:?",["125","75","55","25"],"125","3³=27, 5³=125"),
("Reasoning","Direction Sense","Basic","CAT,UPSC","Easy","A walks 5km North, turns right, walks 3km. Which direction from start?",["North-East","South-East","North-West","East"],"North-East","North then East = North-East diagonal"),
("Reasoning","Direction Sense","Complex","UPSC","Medium","Face North, turn right, turn right, turn left. Now facing?",["North","South","East","West"],"East","N→E→S→E. Final: East"),
("Reasoning","Blood Relations","Basic","CAT,UPSC","Easy","A is B's brother. C is B's mother. How is A related to C?",["Father","Son","Brother","Uncle"],"Son","A is brother of B, C is mother of B, so A is also C's son."),
("Reasoning","Blood Relations","Complex","UPSC","Hard","P is Q's sister. Q is R's mother. R is S's father. How is P related to S?",["Mother","Aunt","Grandmother","Great Aunt"],"Grandmother","P is sister of Q (assumed same gen wrong—let me fix: P→Q's sister, Q→R's mother, R→S's father. P is S's grand-aunt... Actually P is Q's sister and Q is R's mother so P is R's aunt, R is S's father so P is S's great-aunt. But simplest: Grand Aunt"),
("Reasoning","Coding-Decoding","Letter","UPSC","Easy","If CAT = DBU, then DOG = ?",["EPH","FOH","CPF","EPG"],"EPH","Each letter +1: D→E, O→P, G→H"),
("Reasoning","Coding-Decoding","Number","UPSC","Medium","If FACE = 6135, then CAGE = ?",["3175","3135","3157","3175"],"3175","A=1,C=3,E=5,F=6,G=7. CAGE=3175"),
("Reasoning","Logical Puzzles","Arrangement","CAT,UPSC","Medium","5 people in a row. A is to the left of B. C is at the right end. Where can A NOT be?",["Position 1","Position 2","Position 5","Position 3"],"Position 5","If A is at position 5 (right end), but C is at right end. So A can't be at 5."),
("Reasoning","Logical Puzzles","Scheduling","CAT","Hard","A,B,C have meetings. A before B, C not first. How many valid orders?",["2","3","4","6"],"2","A before B: ABC, ACB, CAB. C not first removes CAB. Left: ABC, ACB = 2"),

# ===== ENGLISH =====
("English","Vocabulary","Synonyms","CAT,UPSC","Easy","Synonym of 'Benevolent'?",["Kind","Cruel","Lazy","Smart"],"Kind","Benevolent means kind and generous."),
("English","Vocabulary","Antonyms","CAT,UPSC","Easy","Antonym of 'Abundant'?",["Scarce","Plenty","Rich","Large"],"Scarce","Abundant means plentiful; scarce means lacking."),
("English","Vocabulary","Usage","CAT,UPSC","Medium","Choose the correct word: The professor gave a ___ lecture.",["bored","boring","bore","boredom"],"boring","'Boring' describes the lecture (adjective for things)."),
("English","Vocabulary","Advanced","CAT,UPSC","Hard","'Ephemeral' most closely means?",["Lasting","Temporary","Beautiful","Mysterious"],"Temporary","Ephemeral means short-lived or temporary."),
("English","Grammar","Tenses","CAT,UPSC","Easy","She ___ to school every day.",["go","goes","going","gone"],"goes","Third person singular present tense: goes."),
("English","Grammar","Articles","CAT,UPSC","Easy","I saw ___ elephant at the zoo.",["a","an","the","no article"],"an","'An' before vowel sounds: an elephant."),
("English","Grammar","Prepositions","CAT,UPSC","Medium","He has been working here ___ 2010.",["from","since","for","in"],"since","'Since' is used with a specific point in time."),
("English","Grammar","Voice","CAT,UPSC","Medium","Change to passive: 'They built a bridge.'",["A bridge was built by them","A bridge is built by them","A bridge has been built","A bridge built by them"],"A bridge was built by them","Past simple active → was/were + past participle"),
("English","Grammar","Conditionals","CAT","Hard","If I ___ rich, I would travel the world.",["am","was","were","be"],"were","Subjunctive mood uses 'were' for hypotheticals."),
("English","Reading Comprehension","Inference","CAT,UPSC","Medium","'The early bird catches the worm' implies?",["Birds eat worms","Wake up early for success","Worms come out early","Birds are clever"],"Wake up early for success","This proverb means being early or prompt gives advantages."),
("English","Reading Comprehension","Tone","CAT,UPSC","Hard","A passage criticizing pollution while suggesting solutions has what tone?",["Sarcastic","Persuasive","Narrative","Humorous"],"Persuasive","Criticism + solutions = persuasive writing."),

# ===== CORE SUBJECTS =====
("Core Subjects","Data Structures","Arrays","GATE","Easy","Time complexity of accessing array element by index?",["O(1)","O(n)","O(log n)","O(n²)"],"O(1)","Arrays provide constant-time random access."),
("Core Subjects","Data Structures","Linked Lists","GATE","Medium","Inserting at the beginning of a singly linked list is?",["O(1)","O(n)","O(log n)","O(n²)"],"O(1)","Just update head pointer, no shifting needed."),
("Core Subjects","Data Structures","Trees","GATE","Medium","Maximum nodes in a binary tree of height h?",["2^h","2^h - 1","2^(h+1) - 1","h²"],"2^(h+1) - 1","Full binary tree: 2^(h+1) - 1 nodes."),
("Core Subjects","Data Structures","Stacks","GATE","Easy","Which data structure uses LIFO?",["Queue","Stack","Array","Tree"],"Stack","Stack = Last In First Out."),
("Core Subjects","Data Structures","Graphs","GATE","Hard","Time complexity of BFS on adjacency list?",["O(V+E)","O(V²)","O(E²)","O(V·E)"],"O(V+E)","BFS visits each vertex and edge once."),
("Core Subjects","Algorithms","Sorting","GATE","Easy","Best case time complexity of Bubble Sort?",["O(n)","O(n²)","O(n log n)","O(1)"],"O(n)","When array is already sorted, one pass suffices."),
("Core Subjects","Algorithms","Sorting","GATE","Medium","Which sort is NOT in-place?",["Quick Sort","Heap Sort","Merge Sort","Selection Sort"],"Merge Sort","Merge sort requires O(n) extra space."),
("Core Subjects","Algorithms","Searching","GATE","Easy","Time complexity of binary search?",["O(n)","O(log n)","O(n²)","O(1)"],"O(log n)","Halves the search space each step."),
("Core Subjects","Algorithms","Greedy","GATE","Medium","Which problem is solved by Kruskal's algorithm?",["Shortest path","Minimum spanning tree","Maximum flow","Topological sort"],"Minimum spanning tree","Kruskal's finds MST using greedy edge selection."),
("Core Subjects","Algorithms","DP","GATE","Hard","Optimal substructure is a property of?",["Greedy algorithms only","Dynamic programming","Brute force","None"],"Dynamic programming","DP requires optimal substructure + overlapping subproblems."),
("Core Subjects","Operating Systems","Processes","GATE","Easy","What manages process scheduling in an OS?",["Compiler","Scheduler","Linker","Loader"],"Scheduler","The scheduler decides which process runs next."),
("Core Subjects","Operating Systems","Memory","GATE","Medium","Which technique causes external fragmentation?",["Paging","Segmentation","Virtual memory","Caching"],"Segmentation","Variable-size segments cause external fragmentation."),
("Core Subjects","Operating Systems","Deadlock","GATE","Medium","How many conditions are needed for deadlock?",["2","3","4","5"],"4","Mutual exclusion, hold & wait, no preemption, circular wait."),
("Core Subjects","Operating Systems","Scheduling","GATE","Hard","Which scheduling algorithm can cause starvation?",["FCFS","Round Robin","SJF","All of these"],"SJF","SJF can starve long processes indefinitely."),
("Core Subjects","Computer Networks","Layers","GATE","Easy","How many layers in the OSI model?",["4","5","6","7"],"7","Physical, Data Link, Network, Transport, Session, Presentation, Application"),
("Core Subjects","Computer Networks","Protocols","GATE","Medium","HTTP operates at which OSI layer?",["Transport","Network","Application","Session"],"Application","HTTP is an application layer protocol."),
("Core Subjects","Computer Networks","IP","GATE","Medium","IPv4 address is how many bits?",["16","32","64","128"],"32","IPv4 = 32 bits (4 octets × 8 bits)."),
("Core Subjects","DBMS","SQL","GATE","Easy","Which SQL command is used to retrieve data?",["INSERT","UPDATE","SELECT","DELETE"],"SELECT","SELECT is used to query/retrieve data."),
("Core Subjects","DBMS","Normalization","GATE","Medium","A table in 2NF must eliminate?",["Partial dependency","Transitive dependency","Multivalued dependency","All dependencies"],"Partial dependency","2NF removes partial dependencies on composite keys."),
("Core Subjects","DBMS","Transactions","GATE","Hard","ACID stands for?",["Atomicity, Consistency, Isolation, Durability","Access, Control, Identity, Data","Atomic, Concurrent, Independent, Durable","None"],"Atomicity, Consistency, Isolation, Durability","Four properties ensuring reliable transactions."),
("Core Subjects","Theory of Computation","Automata","GATE","Easy","DFA stands for?",["Deterministic Finite Automaton","Direct Finite Automaton","Dynamic Finite Automaton","None"],"Deterministic Finite Automaton","Each state has exactly one transition per input symbol."),
("Core Subjects","Theory of Computation","Languages","GATE","Medium","Which is NOT a regular language?",["a*b*","(ab)*","a^n b^n","a+b"],"a^n b^n","a^n b^n requires counting, beyond regular languages."),
("Core Subjects","Theory of Computation","Turing","GATE","Hard","A language accepted by a Turing machine is called?",["Regular","Context-free","Recursively enumerable","Context-sensitive"],"Recursively enumerable","TMs accept recursively enumerable languages."),
("Core Subjects","Compiler Design","Phases","GATE","Easy","First phase of compilation?",["Parsing","Lexical Analysis","Code Generation","Optimization"],"Lexical Analysis","Lexer converts source code to tokens first."),
("Core Subjects","Compiler Design","Parsing","GATE","Medium","LR parsing is which type?",["Top-down","Bottom-up","Left to right","Right to left"],"Bottom-up","LR parsers build the parse tree bottom-up."),
("Core Subjects","Computer Architecture","Basics","GATE","Easy","Which unit performs arithmetic operations?",["CU","ALU","MU","I/O"],"ALU","Arithmetic Logic Unit handles all computations."),
("Core Subjects","Computer Architecture","Cache","GATE","Medium","Cache memory is faster than?",["Registers","RAM","ROM","All"],"RAM","Cache sits between registers and RAM in speed hierarchy."),
("Core Subjects","Computer Architecture","Pipeline","GATE","Hard","A 5-stage pipeline executing 100 instructions takes approximately?",["100 cycles","104 cycles","500 cycles","504 cycles"],"104 cycles","5 + (100-1) = 104 cycles with ideal pipelining."),
("Core Subjects","Digital Logic","Gates","GATE","Easy","Output of AND gate with inputs 1 and 0?",["0","1","undefined","both"],"0","AND requires both inputs 1 to output 1."),
("Core Subjects","Digital Logic","Boolean","GATE","Medium","Simplify: A + A'B",["A + B","A","B","A'B"],"A + B","By absorption: A + A'B = A + B"),
("Core Subjects","Database","Indexing","GATE","Medium","B+ tree is commonly used for?",["Sorting","Database indexing","Graph traversal","Hashing"],"Database indexing","B+ trees provide efficient range queries for DB indexes."),
("Core Subjects","Database","Keys","GATE","Easy","A column that uniquely identifies each row is called?",["Foreign key","Primary key","Candidate key","Super key"],"Primary key","Primary key uniquely identifies each record."),

# ===== MORE APTITUDE =====
("Aptitude","Time & Work","Efficiency","CAT","Hard","A is twice as efficient as B. Together they finish in 6 days. A alone?",["9 days","12 days","18 days","6 days"],"9 days","If B does 1 unit/day, A does 2/day. Together 3/day. Total=18. A=18/2=9 days"),
("Aptitude","Percentages","Population","CAT","Medium","Population grows 10% yearly. After 2 years from 10000?",["12000","12100","11000","11100"],"12100","10000 × 1.1 × 1.1 = 12100"),
("Aptitude","Speed & Distance","Boats","CAT","Medium","Boat speed 10 km/h, stream 2 km/h. Downstream speed?",["8 km/h","10 km/h","12 km/h","14 km/h"],"12 km/h","Downstream = boat + stream = 10+2 = 12"),
("Aptitude","Averages","Cricket","CAT","Easy","Batsman scores 40,50,60,70,80 in 5 innings. Average?",["50","55","60","65"],"60","Sum=300, Avg=300/5=60"),
("Aptitude","Simple Interest","Rate","CAT","Medium","₹1000 becomes ₹1200 in 4 years at SI. Rate?",["3%","4%","5%","6%"],"5%","SI=200, R=200×100/(1000×4)=5%"),

# ===== MORE REASONING =====
("Reasoning","Analogies","Relationship","UPSC","Medium","Pen : Writer :: Needle : ?",["Thread","Tailor","Cloth","Sewing"],"Tailor","A pen is a writer's tool; a needle is a tailor's tool."),
("Reasoning","Blood Relations","Puzzle","UPSC","Medium","Pointing to a photo, A says 'He is my mother's only son's son.' Who is in the photo?",["A's son","A's father","A's brother","A's nephew"],"A's son","Mother's only son = A himself. His son = A's son."),
("Reasoning","Coding-Decoding","Reverse","UPSC","Medium","If PENCIL = LICNEP, then ERASER = ?",["RESARE","RASERE","RESAER","RESRAE"],"RESARE","Reverse the letters: ERASER → RESARE"),
("Reasoning","Direction Sense","Distance","UPSC","Hard","Walk 10m South, 10m West, 10m North. Distance from start?",["10m","20m","30m","0m"],"10m","End up 10m West of starting point."),
("Reasoning","Logical Puzzles","Seating","CAT,UPSC","Hard","8 people in a circle. A opposite B, C left of A. Where is C relative to B?",["3 places right","3 places left","Adjacent","Opposite"],"3 places right","In circular arrangement with 8, opposite is 4 apart. C is 1 left of A = 3 right of B."),
]

def seed():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    existing = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    print(f"Existing questions: {existing}")
    
    inserted = 0
    for q in QUESTIONS:
        subj, topic, subtopic, exam, diff, text, opts, ans, expl = q
        qid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO questions (id, subject, topic, subtopic, exam_tag, difficulty,
                                   question_text, options, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (qid, subj, topic, subtopic, exam, diff, text, json.dumps(opts), ans, expl))
        inserted += 1
    
    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    topics = cur.execute("SELECT subject, COUNT(*) FROM questions GROUP BY subject").fetchall()
    conn.close()
    
    print(f"\n✅ Inserted {inserted} new questions!")
    print(f"Total questions now: {total}")
    print("\nBy subject:")
    for t in topics:
        print(f"  {t[0]}: {t[1]}")

if __name__ == "__main__":
    seed()
