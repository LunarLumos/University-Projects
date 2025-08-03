

                                     CERBERON CYBER ANALYZER                
                           Author: Aifee Aadil | Supervisor: Adnan Jihad
             

OVERVIEW
--------

Cerberon is an interactive educational platform designed to bridge the gap between
theory and practice in cybersecurity and algorithms. By simulating real-world
cyber attack and defense scenarios using classical algorithms, Cerberon provides
learners with a hands-on way to understand and experiment with cybersecurity concepts.

Powered by a Python backend and a lightweight web frontend, the platform
demonstrates algorithms such as Dijkstra’s, Bellman-Ford, Merge Sort,
DFS, BFS, Binary Search, and the Travelling Salesman Problem (TSP) in action.

FEATURES
--------

1. Password Attack Simulator
   - Algorithms: Binary Search, Linear Search
   - Simulates brute-force and binary search methods to guess passwords,
     highlighting efficiency differences.

2. Log File Sorter
   - Algorithm: Merge Sort
   - Organizes security log data by time and severity to aid in anomaly detection.

3. Alert Tree Explorer
   - Algorithms: Tree Traversals (In-order, Pre-order, Post-order)
   - Visualizes hierarchical security alerts to better understand threat relationships.

4. Phishing Path Tracker
   - Algorithms: BFS, DFS
   - Traces phishing URL redirection paths, illustrating attacker tactics.

5. Safe Network Path Finder
   - Algorithm: Dijkstra’s Algorithm
   - Finds the shortest or safest route within a network graph.

6. Suspicious Delay Detection
   - Algorithm: Bellman-Ford
   - Detects irregular network delays that could indicate compromised paths.

7. Hacker Movement Optimizer
   - Algorithm: Travelling Salesman Problem (TSP)
   - Models optimal hacker routes to visit multiple targets efficiently.

TECHNICAL ARCHITECTURE
----------------------

Frontend:
- HTML, CSS, JavaScript based UI.
- Modular design allowing selection of individual algorithm modules.
- Dynamic visualization of results for intuitive learning.

Backend:
- Python-driven core logic implementing all algorithms.
- REST API endpoints to receive inputs and return results.
- Processes data such as logs, network maps, passwords.

DATA FLOW
---------

User Input --> Frontend --> REST API Request --> Python Backend
--> Algorithm Execution --> Results --> JSON Response --> Frontend
--> Visualization

EDUCATIONAL VALUE
-----------------

- Demonstrates practical uses of classic algorithms within cybersecurity.
- Allows learners to experiment interactively, reinforcing understanding.
- Supports teaching by providing live examples and visual aids.
- Facilitates comparison of algorithm performance and behavior.
- Encourages exploration and self-driven learning.

INSTALLATION & RUNNING
----------------------

1. Clone the repository:
   git clone https://github.com/yourusername/cerberon.git

2. Navigate into project directory:
   cd cerberon

3. Create and activate virtual environment:
   python -m venv venv
   source venv/bin/activate     (Windows: venv\Scripts\activate)

4. Install required packages:
   pip install -r requirements.txt

5. Launch the backend server:
   python backend/main.py

6. Open frontend/index.html in a web browser.

USAGE INSTRUCTIONS
------------------

- Launch the frontend in your browser.
- Use the sidebar to select the module you want to explore.
- Enter relevant inputs (e.g., password text, network nodes, logs).
- Click 'Run' or 'Simulate' to execute the algorithm.
- View results and visualizations directly in the interface.
- Experiment with different inputs and compare outcomes.

DEMO VIDEO
----------

Watch Cerberon in action!  
[Demo Video Link]: https://youtu.be/

FUTURE IMPROVEMENTS
-------------------

- Real-time network log ingestion.
- Machine learning based threat detection.
- User authentication and progress tracking.
- Exportable reports in PDF or CSV formats.
- Gamified learning experience with points and badges.

ACKNOWLEDGEMENTS
----------------

Sincere thanks to Supervisor Adnan Jihad for guidance and support throughout
the project development.

REFERENCES
----------

- Cormen, T. H. et al. "Introduction to Algorithms." MIT Press, 2009.
- Stallings, W. "Network Security Essentials." Pearson, 2020.
- Tanenbaum, A. S. & Wetherall, D. J. "Computer Networks." Pearson, 2011.
- Bishop, M. "Introduction to Computer Security." Addison-Wesley, 2005.

CONTACT
-------

Author: Aifee Aadil  
GitHub: https://github.com/LunarLumos  
LinkedIn: https://linkedin.com/in/aifeeaadil


                                         MADE WITH LOVE BY LUNAR LABS               

