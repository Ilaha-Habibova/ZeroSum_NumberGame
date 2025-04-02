import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
from math import inf
BG_COLOR, PRIMARY_COLOR, ACCENT_COLOR = "#1E1E1E", "#2A2D3E", "#4E9F3D"
TEXT_COLOR, ENTRY_COLOR, ENTRY_TEXT_COLOR = "#FFFFFF", "#FFFFFF", "#000000"
SECONDARY_COLOR, BUTTON_COLOR, BUTTON_HOVER = "#3A3F5A", "#4E9F3D", "#3D7A2D"
WARNING_COLOR, INFO_COLOR = "#D32F2F", "#2196F3"

#Represents each node in our game tree
class GameState:
    def __init__(self, number, human_score=0, computer_score=0, is_human_turn=True, parent=None):
        self.number, self.human_score, self.computer_score = number, human_score, computer_score
        self.is_human_turn, self.parent, self.children, self.depth = is_human_turn, parent, [], 0 if parent is None else parent.depth + 1

    def add_child(self, child): self.children.append(child)
    def is_terminal(self): return self.number >= 1200

# Heuristic evaluation function
    def get_score(self):
        if self.is_terminal():
            return inf if self.computer_score > self.human_score else -inf if self.computer_score < self.human_score else 0
        
        score_difference = self.computer_score - self.human_score
        progress_factor = self.number / 1200
    
        return score_difference * 2 + progress_factor * 0.5

# Game history,statistics:
class GameHistory:
    def __init__(self): 
        self.history, self.history_file = [], "game_history.dat"
        self.load_history()
    
    def add_result(self, **kwargs):
        kwargs["timestamp"] = time.time()
        self.history.append(kwargs)
        self.save_history()
    
    def get_summary(self): return self.history
    
    def clear_history(self): 
        self.history = []
        self.save_history()
    
    def delete_game(self, index):
        if 0 <= index < len(self.history): 
            self.history.pop(index)
            self.save_history()
            return True
        return False
    
    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                for e in self.history:
                    f.write(f"{e['result']},{e['initial_number']},{e['nodes_visited']},"
                            f"{e['avg_time']},{e['algorithm']},{e['starting_player']},{e['timestamp']}\n")
        except Exception as e: print(f"Error saving history: {e}")
    
    def load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                self.history = [{
                    "result": p[0], "initial_number": int(p[1]), "nodes_visited": int(p[2]),
                    "avg_time": float(p[3]), "algorithm": p[4], "starting_player": p[5],
                    "timestamp": float(p[6])
                } for line in f if len(p := line.strip().split(',')) == 7]
        except FileNotFoundError: pass
        except Exception as e: print(f"Error loading history: {e}")

class NumberGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reach 1200 first!")
        self.root.geometry("900x700")
        self.center_window()
        self.root.minsize(800, 600)  
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 12))
        self.style.configure('TFrame', background=PRIMARY_COLOR)
        self.style.configure('Game.TFrame', background=SECONDARY_COLOR)
        self.style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'), foreground=ACCENT_COLOR)
        self.style.configure('Subheader.TLabel', font=('Helvetica', 16), foreground=TEXT_COLOR)
        self.style.configure('GameInfo.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('TButton', font=('Helvetica', 12, 'bold'), background=BUTTON_COLOR, foreground=TEXT_COLOR)
        self.style.map('TButton', background=[('active', BUTTON_HOVER)])
        self.style.configure('Warning.TLabel', foreground=WARNING_COLOR)
        self.style.configure('Info.TLabel', foreground=INFO_COLOR)
        self.style.configure('TEntry', fieldbackground=ENTRY_COLOR, foreground=ENTRY_TEXT_COLOR) 
        self.initialize_game_variables()
        self.create_welcome_screen()

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def initialize_game_variables(self):
        self.initial_number = self.turn_number = 1
        self.current_state = self.game_tree = None
        self.starting_player = self.algorithm = ""
        self.is_human_turn = True
        self.nodes_visited = self.total_nodes_visited = 0
        self.computer_move_count = self.total_computer_time = 0
        self.game_history = GameHistory()
        self.result_window = None
        self.warning_label = self.given_number_label = self.calculation_label = None
        self.table_labels = []
        self.next_button = None
        self.multiplier_buttons = []

    # WELCOME SCREEN IMPLEMENTATION
    def create_welcome_screen(self):
        self.clear_screen()
        self.show_number_entry_screen()

    def show_number_entry_screen(self):
        self.clear_screen()
        main_frame = ttk.Frame(self.root, padding=40, style='Game.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(main_frame, text="STEP 1: ENTER STARTING NUMBER", style='Header.TLabel').pack(pady=(0, 20))
        ttk.Label(main_frame, text="Choose a number between 8 and 18", style='Subheader.TLabel').pack(pady=(0, 40))
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=15)
        ttk.Label(input_frame, text="Starting Number:", style='Subheader.TLabel').grid(row=0, column=0, padx=10, sticky="w")
        self.number_entry = ttk.Entry(input_frame, width=10, font=('Helvetica', 12))
        self.number_entry.grid(row=0, column=1, padx=10)
        self.number_entry.focus()
        self.warning_label = ttk.Label(main_frame, text="", style='Warning.TLabel')
        self.warning_label.pack(pady=5)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="NEXT", command=self.validate_number_and_proceed, width=20).pack(pady=15)
        ttk.Button(button_frame, text="VIEW STATISTICS", command=self.display_experiment_results, width=20).pack(pady=15)

    def show_player_selection_screen(self):
        self.clear_screen()
        main_frame = ttk.Frame(self.root, padding=40, style='Game.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH) 
        ttk.Label(main_frame, text="STEP 2: SELECT STARTING PLAYER", style='Header.TLabel').pack(pady=(0, 20))
        ttk.Label(main_frame, text="Who should make the first move?", style='Subheader.TLabel').pack(pady=(0, 40))
        player_frame = ttk.Frame(main_frame)
        player_frame.pack(pady=15)
        self.player_var = tk.StringVar()
        for i, (text, val) in enumerate([("Human", "human"), ("Computer", "computer")], 1):
            ttk.Radiobutton(player_frame, text=text, variable=self.player_var, value=val, 
                           command=lambda v=val: self.set_starting_player(v)).grid(row=0, column=i, padx=10)
        self.warning_label = ttk.Label(main_frame, text="", style='Warning.TLabel')
        self.warning_label.pack(pady=5)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="BACK", command=self.show_number_entry_screen, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="NEXT", command=self.validate_player_and_proceed, width=20).pack(side=tk.LEFT, padx=10)

    def show_algorithm_selection_screen(self):
        self.clear_screen()
        main_frame = ttk.Frame(self.root, padding=40, style='Game.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(main_frame, text="STEP 3: SELECT ALGORITHM", style='Header.TLabel').pack(pady=(0, 20))
        ttk.Label(main_frame, text="Choose the AI algorithm to use", style='Subheader.TLabel').pack(pady=(0, 40))
        algo_frame = ttk.Frame(main_frame)
        algo_frame.pack(pady=15)
        self.algo_var = tk.StringVar()
        for i, (text, val) in enumerate([("Minimax", "minimax"), ("Alpha-Beta", "alphabeta")], 1):
            ttk.Radiobutton(algo_frame, text=text, variable=self.algo_var, value=val,
                           command=lambda v=val: self.set_algorithm(v)).grid(row=0, column=i, padx=10)
        self.warning_label = ttk.Label(main_frame, text="", style='Warning.TLabel')
        self.warning_label.pack(pady=5)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20) 
        ttk.Button(button_frame, text="BACK", command=self.show_player_selection_screen, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="BEGIN GAME", command=self.validate_algorithm_and_start, width=20).pack(side=tk.LEFT, padx=10)

    def validate_number_and_proceed(self):
        try:
            self.initial_number = int(self.number_entry.get())
            if not 8 <= self.initial_number <= 18:
                self.warning_label.config(text="Number must be between 8 and 18")
                return
            self.show_player_selection_screen()
        except ValueError:
            self.warning_label.config(text="Please enter a valid number")

    def validate_player_and_proceed(self):
        if not self.starting_player:
            self.warning_label.config(text="Please select starting player")
            return
        self.show_algorithm_selection_screen()

    def validate_algorithm_and_start(self):
        if not self.algorithm:
            self.warning_label.config(text="Please select algorithm")
            return
        self.start_game_session()

    def set_starting_player(self, player): 
        self.starting_player = player
        self.clear_warning()

    def set_algorithm(self, algorithm): 
        self.algorithm = algorithm
        self.clear_warning()

    def clear_warning(self): 
        if self.warning_label: self.warning_label.config(text="")

    
    def start_game_session(self):
        self.clear_screen()
        self.current_state = GameState(self.initial_number)
        self.game_tree = self.current_state
        self.turn_number = 0
        self.is_human_turn = (self.starting_player == "human")
        self.nodes_visited = self.total_nodes_visited = self.computer_move_count = self.total_computer_time = 0
        self.create_game_screen()
        self.turn_label.config(text=f"TURN {self.turn_number}")
        if not self.is_human_turn: self.root.after(500, self.computer_move)

    def create_game_screen(self):
        main_frame = ttk.Frame(self.root, style='Game.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20) 
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(10, 20))
        ttk.Label(header_frame, text="REACH 1200 FIRST!", style='Header.TLabel').pack(side=tk.LEFT)
        self.turn_label = ttk.Label(header_frame, text=f"TURN {self.turn_number}", style='Subheader.TLabel')
        self.turn_label.pack(side=tk.RIGHT)
        board_frame = ttk.Frame(main_frame, padding=20)
        board_frame.pack(expand=True, fill=tk.BOTH)
        state_frame = ttk.Frame(board_frame)
        state_frame.pack(fill=tk.X, pady=10)
        self.given_number_label = ttk.Label(state_frame, text=f"Given number: {self.current_state.number}", style='GameInfo.TLabel')
        self.given_number_label.pack(anchor=tk.W)
        self.calculation_label = ttk.Label(state_frame, text="", style='GameInfo.TLabel')
        self.calculation_label.pack(anchor=tk.W)
        self.number_label = ttk.Label(state_frame, text=f"Current number: {self.current_state.number}", style='GameInfo.TLabel')
        self.number_label.pack(anchor=tk.W)
        self.score_label = ttk.Label(state_frame, 
                                   text=f"SCORE: Human {self.current_state.human_score} | Computer {self.current_state.computer_score}",
                                   style='GameInfo.TLabel')
        self.score_label.pack(anchor=tk.W, pady=(10, 0))
        self.move_info_label = ttk.Label(board_frame, text="", style='GameInfo.TLabel')
        self.move_info_label.pack(pady=10)
        btn_frame = ttk.Frame(board_frame)
        btn_frame.pack(pady=20)
        self.multiplier_buttons = []
        for m in [2, 3, 4]:
            btn = ttk.Button(btn_frame, text=str(m), command=lambda m=m: self.make_move(m), width=8)
            btn.pack(side=tk.LEFT, padx=15)
            self.multiplier_buttons.append(btn)
        self.next_button = ttk.Button(board_frame, text="NEXT TURN", command=self.next_turn)
        self.next_button.pack(pady=15)
        self.next_button.pack_forget()
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(footer_frame, text="STATISTICS", command=self.display_experiment_results).pack(side=tk.RIGHT, padx=10)
        ttk.Button(footer_frame, text="NEW GAME", command=self.create_welcome_screen).pack(side=tk.RIGHT, padx=10)

    def make_move(self, multiplier):
        if self.is_human_turn:
            self.update_game_state(multiplier, "Human")
            self.is_human_turn = False
            for btn in self.multiplier_buttons: btn.state(['disabled'])
            
            if not self.current_state.is_terminal():
                self.next_button.pack(pady=15)
                self.turn_number += 1
                self.turn_label.config(text=f"TURN {self.turn_number}")
            else:
                self.turn_number += 1
                self.turn_label.config(text=f"TURN {self.turn_number}")
                self.root.after(1000, self.end_game)

    def next_turn(self):
        self.next_button.pack_forget()
        self.computer_move()

    def computer_move(self):
        for btn in self.multiplier_buttons: btn.state(['!disabled'])
        self.nodes_visited = 0
        start_time = time.perf_counter()

        if self.algorithm == "minimax":
            best_multiplier, _ = self.minimax(self.current_state, depth=3, is_maximizing=True)
        else:
            best_multiplier, _ = self.alphabeta(self.current_state, depth=3, alpha=-inf, beta=inf, is_maximizing=True)

        self.total_computer_time += time.perf_counter() - start_time
        self.computer_move_count += 1
        self.total_nodes_visited += self.nodes_visited
        self.update_game_state(best_multiplier, "Computer")
        self.is_human_turn = True
        
        if self.current_state.is_terminal():
            self.turn_number += 1
            self.turn_label.config(text=f"TURN {self.turn_number}")
            self.root.after(1000, self.end_game)
        else:
            self.next_button.pack_forget()
            self.turn_number += 1
            self.turn_label.config(text=f"TURN {self.turn_number}")

# Algorithms implementation:
    def minimax(self, state, depth, is_maximizing):
        self.nodes_visited += 1
        if depth == 0 or state.is_terminal():
            return None, state.get_score()
        
        best_score = -inf if is_maximizing else inf
        best_multiplier = None
        
        for m in [2, 3, 4]:
            new_state = self.apply_move(state, m, not is_maximizing)
            _, score = self.minimax(new_state, depth-1, not is_maximizing)
            
            if (is_maximizing and score > best_score) or (not is_maximizing and score < best_score) or best_multiplier is None:
                best_score, best_multiplier = score, m
                    
        return best_multiplier, best_score

    def alphabeta(self, state, depth, alpha, beta, is_maximizing):
        self.nodes_visited += 1
        if depth == 0 or state.is_terminal():
            return None, state.get_score()
        
        best_score = -inf if is_maximizing else inf
        best_multiplier = None
        
        for m in [2, 3, 4]:
            new_state = self.apply_move(state, m, not is_maximizing)
            _, score = self.alphabeta(new_state, depth-1, alpha, beta, not is_maximizing)
            
            if is_maximizing:
                if score > best_score or best_multiplier is None:
                    best_score, best_multiplier = score, m
                alpha = max(alpha, best_score)
            else:
                if score < best_score or best_multiplier is None:
                    best_score, best_multiplier = score, m
                beta = min(beta, best_score)
            
            if beta <= alpha:
                break
                
        return best_multiplier, best_score

    # Game mechanism:
    def apply_move(self, state, multiplier, is_human=True):
        new_number = state.number * multiplier
        hs, cs = state.human_score, state.computer_score
        
        if new_number % 2 == 0:
            hs, cs = (hs, cs-1) if is_human else (hs-1, cs)
        else:
            hs, cs = (hs+1, cs) if is_human else (hs, cs+1)

        new_state = GameState(new_number, hs, cs, not is_human, state)
        state.add_child(new_state)
        return new_state

    def update_game_state(self, multiplier, player):
        prev_num = self.current_state.number
        self.current_state = self.apply_move(self.current_state, multiplier, player=="Human")
        opponent = "Computer" if player == "Human" else "Human"
        self.given_number_label.config(text=f"Given number: {prev_num}")
        self.calculation_label.config(text=f"Calculation: {prev_num} × {multiplier} = {self.current_state.number}")
        self.number_label.config(text=f"Current number: {self.current_state.number}")
        
        if self.current_state.number % 2 == 0:
            msg = f"{player} chose {multiplier}. Even number! {opponent} loses 1 point"
            self.move_info_label.config(text=msg, foreground=WARNING_COLOR)
        else:
            msg = f"{player} chose {multiplier}. Odd number! {player} gains 1 point"
            self.move_info_label.config(text=msg, foreground=ACCENT_COLOR)
            
        self.score_label.config(text=f"SCORE: Human {self.current_state.human_score} | Computer {self.current_state.computer_score}")

    def end_game(self):
        for btn in self.multiplier_buttons: btn.state(['disabled'])
        self.next_button.pack_forget()

        if self.current_state.human_score > self.current_state.computer_score:
            result, color = "HUMAN WINS!", ACCENT_COLOR
        elif self.current_state.human_score < self.current_state.computer_score:
            result, color = "COMPUTER WINS!", WARNING_COLOR
        else:
            result, color = "DRAW!", INFO_COLOR
        avg_time = self.total_computer_time / self.computer_move_count if self.computer_move_count > 0 else 0
        self.game_history.add_result(
            result=result.split('!')[0], initial_number=self.initial_number,
            nodes_visited=self.total_nodes_visited, avg_time=avg_time,
            algorithm=self.algorithm, starting_player=self.starting_player
        )
        self.move_info_label.config(text=f"GAME OVER - {result}", foreground=color)
        time_frame = ttk.Frame(self.root)
        time_frame.pack(pady=10)
        ttk.Label(time_frame, text=f"Avg. time per move: {avg_time:.6f}s").pack()

        if hasattr(self, 'result_window') and self.result_window and self.result_window.winfo_exists():
            self.update_results_table()

    def display_experiment_results(self):
        if not hasattr(self, 'game_history'): return
        summary = self.game_history.get_summary()
        if self.result_window is not None and self.result_window.winfo_exists():
            self.result_window.lift()
            return
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title("Game Statistics")
        self.result_window.geometry("1000x700")
        self.result_window.minsize(900, 600)
        self.result_window.configure(bg=BG_COLOR)
        self.result_window.update_idletasks()
        w, h = self.result_window.winfo_width(), self.result_window.winfo_height()
        x = (self.result_window.winfo_screenwidth() - w) // 2
        y = (self.result_window.winfo_screenheight() - h) // 2
        self.result_window.geometry(f'+{x}+{y}')
        container = ttk.Frame(self.result_window, padding=20, style='Game.TFrame')
        container.pack(expand=True, fill=tk.BOTH)
        ttk.Label(container, text="GAME STATISTICS", style='Header.TLabel').pack(pady=(0, 20))
        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        total_games = len(summary)
        stats = [
            f"Total Games: {total_games}",
            f"Human Wins: {sum(1 for g in summary if g['result'] == 'HUMAN WINS')}",
            f"Computer Wins: {sum(1 for g in summary if g['result'] == 'COMPUTER WINS')}",
            f"Draws: {sum(1 for g in summary if g['result'] == 'DRAW')}",
            f"Minimax Games: {sum(1 for g in summary if g['algorithm'] == 'minimax')}",
            f"Alpha-Beta Games: {sum(1 for g in summary if g['algorithm'] == 'alphabeta')}"
        ]
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text=stat, style='Subheader.TLabel').grid(row=i//3, column=i%3, sticky="w", padx=20, pady=5)
        table_container = ttk.Frame(container)
        table_container.pack(expand=True, fill=tk.BOTH)
        canvas = tk.Canvas(table_container, bg=SECONDARY_COLOR, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        headers = ["#", "Result", "Initial", "Starter", "Algorithm", "Nodes", "Time (s)", "Date"]
        for col, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, font=('Helvetica', 11, 'bold'), 
                     background=PRIMARY_COLOR, padding=8).grid(row=0, column=col, sticky="nsew")
        self.table_labels = []
        for row, game in enumerate(summary, 1):
            bg = SECONDARY_COLOR if row % 2 == 0 else BG_COLOR
            time_str = f"{game['avg_time']:.6f}".rstrip('0').rstrip('.') if '.' in f"{game['avg_time']:.6f}" else f"{game['avg_time']:.6f}"
            date_str = time.strftime('%d/%m %H:%M', time.localtime(game['timestamp']))
            cols = [str(row), game['result'], str(game['initial_number']), 
                   game['starting_player'].title(), game['algorithm'].title(), 
                   str(game['nodes_visited']), time_str, date_str]
            row_labels = []
            for col, text in enumerate(cols):
                label = ttk.Label(scrollable_frame, text=text, background=bg, padding=8)
                label.grid(row=row, column=col, sticky="nsew")
                row_labels.append(label)
            self.table_labels.append(row_labels)

        for i in range(len(headers)):
            scrollable_frame.grid_columnconfigure(i, weight=1)
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=(20, 0))
        ttk.Button(btn_frame, text="DELETE SELECTED", command=self.delete_selected_game).pack(side=tk.LEFT, padx=15)
        ttk.Button(btn_frame, text="CLEAR HISTORY", command=self.clear_all_history).pack(side=tk.LEFT, padx=15)
        self.result_window.protocol("WM_DELETE_WINDOW", self.on_results_close)

    def on_results_close(self):
        if self.result_window:
            self.result_window.destroy()
            self.result_window = None

    def delete_selected_game(self):
        try:
            selected = simpledialog.askstring("Delete Game", "Enter game number to delete:", parent=self.result_window)
            if selected is None: return
        
            selected_index = int(selected) - 1
            if self.game_history.delete_game(selected_index):
                self.result_window.destroy()
                self.result_window = None
                self.display_experiment_results()  
            else:
                messagebox.showwarning("Invalid Selection", "Please enter a valid game number", parent=self.result_window)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number", parent=self.result_window)

    def clear_all_history(self):
        if messagebox.askyesno("Confirm", "Clear all game history?", parent=self.result_window):
            self.game_history.clear_history()
            self.update_results_table()

    def update_results_table(self):
        if not hasattr(self, 'result_window') or not self.result_window.winfo_exists():
            return
            
        summary = self.game_history.get_summary()
        
        for row_labels in self.table_labels:
            for label in row_labels: label.destroy()
        self.table_labels = []
        
        try:
            scrollable_frame = self.result_window.winfo_children()[0].winfo_children()[3].winfo_children()[0]
            headers = ["#", "Result", "Initial", "Starter", "Algorithm", "Nodes", "Time (s)", "Date"]
            for col, header in enumerate(headers):
                ttk.Label(scrollable_frame, text=header, font=('Helvetica', 11, 'bold'), 
                         background=PRIMARY_COLOR, padding=8).grid(row=0, column=col, sticky="nsew")
            
            for row, game in enumerate(summary, 1):
                bg = SECONDARY_COLOR if row % 2 == 0 else BG_COLOR
                time_str = f"{game['avg_time']:.6f}".rstrip('0').rstrip('.') if '.' in f"{game['avg_time']:.6f}" else f"{game['avg_time']:.6f}"
                date_str = time.strftime('%d/%m %H:%M', time.localtime(game['timestamp']))
                cols = [str(row), game['result'], str(game['initial_number']), 
                       game['starting_player'].title(), game['algorithm'].title(), 
                       str(game['nodes_visited']), time_str, date_str]
                row_labels = []
                for col, text in enumerate(cols):
                    label = ttk.Label(scrollable_frame, text=text, background=bg, padding=8)
                    label.grid(row=row, column=col, sticky="nsew")
                    row_labels.append(label)
                self.table_labels.append(row_labels)
            for i in range(len(headers)):
                scrollable_frame.grid_columnconfigure(i, weight=1)    
        except Exception as e: print(f"Error updating results table: {e}")

    def clear_screen(self, window=None):
        target = window if window else self.root
        for widget in target.winfo_children(): widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGameGUI(root)
    root.mainloop()