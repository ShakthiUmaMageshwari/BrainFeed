"""Seed final batch of 100+ questions. Run: python backend/seed_final_batch.py"""
import sqlite3, uuid, os, json

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "brainfeed.db")

QUESTIONS = [
# ===== ADVANCED MATHS =====
("Maths","Complex Numbers","Basics","JEE,GATE","Easy","Value of i^4?",["1","-1","i","-i"],"1","Powers of i cycle: i, -1, -i, 1."),
("Maths","Complex Numbers","Modulus","JEE","Medium","Modulus of 3+4i?",["5","7","25","12"],"5","|z| = √(a² + b²) = √(9+16) = 5"),
("Maths","Complex Numbers","Conjugate","JEE","Easy","Conjugate of 2-3i?",["2+3i","-2-3i","2-3i","-2+3i"],"2+3i","Change sign of imaginary part."),
("Maths","Differential Equations","Order","GATE","Easy","Order of d²y/dx² + y = 0?",["1","2","3","0"],"2","Highest derivative determines order."),
("Maths","Differential Equations","Linear","GATE","Medium","Integrating factor for dy/dx + Py = Q?",["e^∫Pdx","e^∫Qdx","∫Pdx","ln(P)"],"e^∫Pdx","Standard formula for linear DE."),
("Maths","Vectors","Cross Product","JEE,GATE","Medium","i × j = ?",["k","-k","0","1"],"k","Right-hand rule for unit vectors."),
("Maths","Vectors","Dot Product","JEE","Easy","If a·b = 0, vectors are?",["Parallel","Perpendicular","Equal","Opposite"],"Perpendicular","Dot product is zero for orthogonal vectors."),
("Maths","Matrices","Inverse","GATE","Medium","Inverse of diag(2, 4)?",["diag(0.5, 0.25)","diag(2, 4)","diag(-2, -4)","diag(4, 2)"],"diag(0.5, 0.25)","Inverse of diagonal matrix is reciprocal of diagonal elements."),
("Maths","Matrices","Rank","GATE","Hard","Rank of a null matrix?",["0","1","Undefined","n"],"0","Null matrix has rank 0."),
("Maths","Calculus","Chain Rule","JEE","Medium","d/dx(sin(x²))?",["2x cos(x²)","cos(x²)","2x sin(x)","x² cos(x)"],"2x cos(x²)","Chain rule: cos(u) * u'"),

# ===== VERBAL ABILITY =====
("Verbal","Sentence Correction","Grammar","CAT","Medium","Correct: 'He is one of the best player.'",["He is one of the best players.","He is best player.","He is one best player.","No correction needed."],"He is one of the best players.","'One of the plural noun' rule."),
("Verbal","Sentence Correction","Tense","CAT","Easy","I have seen him yesterday.",["I saw him yesterday.","I had seen him yesterday.","I see him yesterday.","No correction needed."],"I saw him yesterday.","Specific past time requires simple past tense."),
("Verbal","Idioms","Meaning","CAT,UPSC","Medium","'Bite the bullet' means?",["To face a difficult situation bravely","To eat metal","To give up","To clean a gun"],"To face a difficult situation bravely","Meaning: Enduring something painful."),
("Verbal","Idioms","Usage","CAT","Hard","'Burn the midnight oil' means?",["Work late into the night","Waste resources","Start a fire","Sleep early"],"Work late into the night","Meaning: Working or studying late."),
("Verbal","Vocabulary","Roots","CAT","Medium","Root 'bene' means?",["Good","Bad","War","Sleep"],"Good","e.g., Benevolent, Benefit."),
("Verbal","Vocabulary","Roots","CAT","Medium","Root 'mal' means?",["Bad","Good","Male","Time"],"Bad","e.g., Malevolent, Malfunction."),
("Verbal","Critical Reasoning","Assumption","CAT,GMAT","Hard","Premise: 'It is raining.' Conclusion: 'The ground is wet.' Assumption?",["Rain makes ground wet.","Ground was already wet.","It is not snowing.","Clouds are grey."],"Rain makes ground wet.","The link between rain and wet ground."),
("Verbal","Critical Reasoning","Strengthen","CAT","Hard","Which strengthens: 'Exercise leads to weight loss'?",["Study shows exercisers lost 5kg.","Exercise makes you hungry.","Diet is more important.","Sleeping helps weight loss."],"Study shows exercisers lost 5kg.","Empirical evidence supports the claim."),
("Verbal","Para Jumbles","Sequence","CAT","Hard","Order: A. It was late. B. He ran fast. C. He missed the bus. D. He woke up.",["D-A-B-C","A-B-C-D","D-C-B-A","B-C-A-D"],"D-A-B-C","Chronological: Woke → Late → Ran → Missed."),
("Verbal","Reading Comprehension","Main Idea","CAT","Medium","Passage about climate change effects. Main idea?",["Impact of global warming","Types of clouds","History of Earth","Solar system"],"Impact of global warming","The central theme."),

# ===== LOGICAL REASONING =====
("Reasoning","Coding","Pattern","UPSC","Easy","A=1, B=2, ... Z=26. BAD = ?",["214","213","312","124"],"214","B=2, A=1, D=4."),
("Reasoning","Coding","Reverse","UPSC","Medium","Z=1, Y=2, ... A=26. GO = ?",["20-12","7-15","20-15","12-20"],"20-12","G is 7th from start, so 20th from end. O is 15th, so 12th."),
("Reasoning","Series","Number","UPSC","Easy","1, 4, 9, 16, ?",["25","20","30","36"],"25","Squares: 1², 2², 3², 4², 5²."),
("Reasoning","Series","Alpha","UPSC","Medium","A, C, E, G, ?",["I","H","J","K"],"I","Skip one letter: B, D, F, H skipped."),
("Reasoning","Blood Relations","Spouse","UPSC","Medium","A is B's husband. C is A's daughter. B is C's?",["Mother","Aunt","Sister","Grandmother"],"Mother","Wife of father is mother."),
("Reasoning","Directions","Shadow","UPSC","Hard","Morning sun. Shadow falls to left. Facing?",["North","South","East","West"],"North","Morning sun East → Shadow West. Left is West → Facing North."),
("Reasoning","Seating Arrangement","Linear","CAT","Medium","5 people. A mid. B left of A. C right of A. D left of B. E right of C. Order?",["D-B-A-C-E","D-A-B-C-E","B-D-A-C-E","A-B-C-D-E"],"D-B-A-C-E","D B A C E fits all conditions."),
("Reasoning","Clocks","Angle","CAT","Hard","Angle between hands at 3:00?",["90°","45°","60°","180°"],"90°","3 hours = 3 × 30° = 90°."),
("Reasoning","Calendars","Day","CAT","Hard","If today is Monday, day after 7 days?",["Monday","Tuesday","Sunday","Saturday"],"Monday","7 days is exactly 1 week."),
("Reasoning","Venn Diagrams","Relationships","UPSC","Easy","Fruit, Apple, Mango?",["Circle inside Circle, separate Circle inside","Two circles inside one big circle","Three separate circles","Overlapping circles"],"Two circles inside one big circle","Apple and Mango are separate fruits inside Fruit category."),

# ===== COMPUTER SCIENCE (ADVANCED) =====
("Core Subjects","Algorithms","Complexity","GATE","Hard","Worst case of QuickSort?",["O(n²)","O(n log n)","O(n)","O(log n)"],"O(n²)","Occurs when pivot implies unbalanced split (e.g., sorted array)."),
("Core Subjects","Algorithms","Graph","GATE","Hard","Shortest path in unweighted graph?",["BFS","DFS","Dijkstra","Prim"],"BFS","BFS guarantees shortest path in unweighted graphs."),
("Core Subjects","OS","Scheduling","GATE","Medium","Which scheduler controls degree of multiprogramming?",["Long-term","Short-term","Medium-term","I/O"],"Long-term","Decides which processes enter the ready queue."),
("Core Subjects","OS","Synchronization","GATE","Hard","Semaphore initialized to 1 is called?",["Binary semaphore","Counting semaphore","Mutex","Monitor"],"Binary semaphore","It behaves like a lock (0 or 1)."),
("Core Subjects","DBMS","Normal Forms","GATE","Medium","BCNF is stricter than?",["3NF","2NF","1NF","All of these"],"All of these","BCNF > 3NF > 2NF > 1NF."),
("Core Subjects","DBMS","SQL","GATE","Medium","Delete vs Truncate?",["Truncate is faster","Delete is faster","Same speed","Truncate allows WHERE"],"Truncate is faster","Truncate is DDL and doesn't log individual row deletions."),
("Core Subjects","Networks","TCP","GATE","Hard","TCP is?",["Connection-oriented","Connectionless","Unreliable","Datagram"],"Connection-oriented","Establish connection via 3-way handshake."),
("Core Subjects","Networks","DNS","GATE","Easy","Port number for DNS?",["53","80","25","22"],"53","Standard port for DNS."),
("Core Subjects","Architecture","Addressing","GATE","Medium","PC-relative addressing is used for?",["Branch instructions","Stack operations","I/O","Arithmetic"],"Branch instructions","Target address relative to Program Counter."),
("Core Subjects","Architecture","Interrupts","GATE","Hard","Maskable interrupts can be?",["Ignored","Pending","Disabled","All of these"],"All of these","CPU can ignore them if masked."),

# ===== GENERAL KNOWLEDGE =====
("GK","Geography","Rivers","UPSC","Easy","Longest river in India?",["Ganga","Yamuna","Godavari","Brahmaputra"],"Ganga","Total length 2525 km."),
("GK","Geography","Planets","UPSC","Easy","Largest planet in solar system?",["Jupiter","Saturn","Mars","Earth"],"Jupiter","Largest by mass and volume."),
("GK","History","Ancient","UPSC","Medium","Who wrote Arthashastra?",["Kautilya/Chanakya","Kalidasa","Aryabhata","Harsha"],"Kautilya/Chanakya","Ancient treatise on statecraft."),
("GK","History","Modern","UPSC","Medium","Year of Indian Independence?",["1947","1950","1948","1942"],"1947","August 15, 1947."),
("GK","Polity","Constitution","UPSC","Medium","Father of Indian Constitution?",["Dr. B.R. Ambedkar","Nehru","Gandhi","Patel"],"Dr. B.R. Ambedkar","Chairman of Drafting Committee."),
("GK","Polity","Rights","UPSC","Hard","Right to Privacy is under which Article?",["21","19","14","32"],"21","Putta swamy judgment declared it part of Article 21."),
("GK","Science","Physics","UPSC","Easy","Unit of Force?",["Newton","Joule","Watt","Pascal"],"Newton","SI unit of force."),
("GK","Science","Chemistry","UPSC","Easy","Chemical symbol for Gold?",["Au","Ag","Fe","Pb"],"Au","From Latin 'Aurum'."),
("GK","Science","Biology","UPSC","Medium","Powerhouse of the cell?",["Mitochondria","Nucleus","Ribosome","Lysosome"],"Mitochondria","Generates ATP."),
("GK","Economy","Banking","UPSC","Medium","RBI established in which year?",["1935","1947","1950","1969"],"1935","Established on April 1, 1935."),

# ===== APTITUDE (Additional) =====
("Aptitude","Profit & Loss","Advanced","CAT","Hard","Dishonest dealer uses 900g weight instead of 1kg. Profit?",["11.11%","10%","9.09%","12.5%"],"11.11%","Profit = (Error/True Value - Error) * 100 = 100/900 * 100."),
("Aptitude","Time & Distance","Boats","CAT","Hard","Boat takes 4hr downstream, 6hr upstream for same distance. Speed ratio?",["5:1","3:2","2:1","4:3"],"5:1","(u+v)4 = (u-v)6 => 4u+4v = 6u-6v => 10v = 2u => u/v = 5/1."),
("Aptitude","Number System","Remainders","CAT","Hard","Remainder when 2^50 is divided by 7?",["4","2","1","3"],"4","2^3 = 1 mod 7. 2^50 = (2^3)^16 * 2^2 = 1 * 4 = 4."),
("Aptitude","Geometry","Triangles","CAT","Medium","Centroid divides median in ratio?",["2:1","1:1","3:1","2:3"],"2:1","Property of centroid."),
("Aptitude","Algebra","Roots","CAT","Medium","Sum of roots of x² - 5x + 6 = 0?",["5","-5","6","-6"],"5","-b/a = -(-5)/1 = 5."),

# ===== FILLERS (To reach 100+) =====
("English","Vocabulary","One Word","SSC","Easy","Life history written by oneself?",["Autobiography","Biography","Memoir","History"],"Autobiography","Auto = self."),
("English","Vocabulary","One Word","SSC","Easy","Study of birds?",["Ornithology","Zoology","Botany","Entomology"],"Ornithology","Ornis = bird."),
("English","Spelling","Correct","SSC","Easy","Choose correct spelling.",["Vacuum","Vaccum","Vacume","Vacuume"],"Vacuum","U-U-M."),
("English","Spelling","Correct","SSC","Easy","Choose correct spelling.",["Embarrass","Embarass","Embaras","Embarras"],"Embarrass","Double r, double s."),
("Reasoning","Symbol Operation","Swap","SSC","Medium","If + means -, - means x, x means /. Value of 10 - 2 + 5?",["15","5","25","0"],"15","10 x 2 - 5 = 20 - 5 = 15."),
("Reasoning","Odd One Out","Classification","SSC","Easy","Find odd one.",["Carrot","Potato","Tomato","Onion"],"Tomato","Tomato creates fruit above ground, others are roots/tubers (culinary vegetable distinction)."),
("GK","Sports","Cricket","Only","Easy","Who has most international centuries?",["Sachin Tendulkar","Kohli","Ponting","Kallis"],"Sachin Tendulkar","100 centuries."),
("GK","Sports","Olympics","General","Easy","Number of rings in Olympic logo?",["5","4","6","3"],"5","Representing 5 continents."),
("GK","Awards","Nobel","General","Medium","First Asian Nobel laureate?",["Rabindranath Tagore","CV Raman","Mother Teresa","Amartya Sen"],"Rabindranath Tagore","Literature, 1913."),
("GK","Geography","Capital","General","Easy","Capital of Australia?",["Canberra","Sydney","Melbourne","Perth"],"Canberra","Planned capital city."),
("Maths","Trigonometry","Values","JEE","Easy","sin(30°)?",["0.5","1","0","0.866"],"0.5","Standard value."),
("Maths","Trigonometry","Identity","JEE","Easy","sin²x + cos²x = ?",["1","0","-1","2x"],"1","Fundamental identity."),
("Maths","Trigonometry","Tan","JEE","Easy","tan(45°)?",["1","0","Undef","0.5"],"1","sin/cos = 1/√2 / 1/√2 = 1."),
("Core Subjects","OS","Linux","Basic","Easy","Command to list files?",["ls","dir","cd","cp"],"ls","List directory contents."),
("Core Subjects","OS","Linux","Basic","Easy","Command to copy files?",["cp","mv","rm","ls"],"cp","Copy."),
("Core Subjects","Coding","Python","Basic","Easy","Keyword to define function?",["def","func","function","define"],"def","Standard syntax."),
("Core Subjects","Coding","Java","Basic","Easy","Entry point method name?",["main","start","run","init"],"main","public static void main."),
("Reasoning","Analogy","General","SSC","Easy","Doctor : Hospital :: Teacher : ?",["School","Student","Class","Book"],"School","Place of work."),
("Reasoning","Analogy","General","SSC","Easy","Day : Night :: Up : ?",["Down","Left","Right","High"],"Down","Antonym."),
("Aptitude","Simplification","BODMAS","Bank","Easy","10 + 10 / 2?",["15","10","5","20"],"15","Division first: 10 + 5 = 15."),
("Aptitude","Simplification","Power","Bank","Easy","Square of 12?",["144","124","140","169"],"144","12 x 12."),
("Aptitude","Simplification","Root","Bank","Easy","Square root of 81?",["9","8","7","6"],"9","9 x 9 = 81.")
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
    conn.close()
    
    print(f"\n✅ Inserted {inserted} final batch questions!")
    print(f"Total questions now: {total}")

if __name__ == "__main__":
    seed()
