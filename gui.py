import tkinter
from gol import GOL


class GUI:
    def __init__(self, initial_board, board_size):
        self.game_speed = 1
        self.first_draw = True
        self.gol = GOL(initial_board, board_size)
        self.iter = 0

        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.root, width=22 * board_size, height=22 * board_size - 30)
        self.canvas.pack()

        self.label = tkinter.Label(self.root, text=f"Iter: 0 | Size: {len(initial_board)}")
        self.label.pack()

        speed_slider = tkinter.Scale(self.root, from_=1, to=100, orient=tkinter.HORIZONTAL,
                                           label='Speed', command=self.speed_control)
        speed_slider.set(self.game_speed)
        speed_slider.pack()
        run_button = tkinter.Button(self.root, text="Run", command=lambda: self.run_and_update(False))
        run_button.pack()
        stable_button = tkinter.Button(self.root, text="Run to stable", command=lambda: self.run_and_update(True))
        stable_button.pack()
        self.update_board()

    def start(self):
        tkinter.mainloop()

    def update_board(self) -> None:
        self.canvas.delete('all')
        for i in range(self.gol.get_board_size()):
            for j in range(self.gol.get_board_size()):
                if self.gol[i, j] == 1:
                    self.canvas.create_rectangle(i * 21, j * 21, i * 21 + 20, j * 21 + 20, fill='chartreuse2')
                else:
                    self.canvas.create_rectangle(i * 21, j * 21, i * 21 + 20, j * 21 + 20, fill='brown4')

    def run_and_update(self, until_stable) -> None:
        self.label.config(text=f"Iter: {self.iter} | Size: {len(self.gol)}")
        if until_stable and self.gol.is_stable:
            return
        self.gol.play_game()
        self.update_board()
        self.root.after(int(1000.0 / self.game_speed), lambda: self.run_and_update(until_stable))
        self.iter += 1

    def speed_control(self, speed):
        self.game_speed = int(speed)


def main():
    initial_board = (((17, 17), 1), ((17, 16), 1), ((18, 17), 1), ((16, 17), 1), ((16, 24), 1), ((16, 23), 1), ((19, 24), 1), ((18, 24), 1), ((19, 22), 1), ((20, 19), 1), ((21, 19), 1), ((23, 18), 1), ((23, 19), 1), ((23, 17), 1), ((22, 16), 1), ((24, 19), 1), ((21, 21), 1), ((20, 23), 1), ((24, 23), 1), ((21, 20), 1), ((20, 21), 1))  # Score(score=170.21866666666668, size=202, time=0.8426666666666667))
    initial_board = (((18, 18), 1), ((19, 19), 1), ((19, 20), 1), ((19, 22), 1), ((18, 22), 1), ((18, 21), 1), ((24, 17), 1), ((20, 20), 1), ((20, 19), 1), ((23, 17), 1), ((22, 18), 1)) # Score(score=157.388, size=231, time=0.6813333333333333))
    initial_board = (((23, 19), 1), ((18, 17), 1), ((21, 18), 1), ((18, 23), 1), ((22, 20), 1), ((20, 18), 1), ((22, 19), 1), ((22, 23), 1), ((17, 20), 1), ((19, 19), 1), ((20, 19), 1), ((18, 19), 1)) # Score(score=182.736, size=188, time=0.972))
    initial_board = (((17, 17), 1), ((18, 19), 1), ((17, 20), 1), ((20, 19), 1), ((24, 16), 1), ((24, 18), 1), ((22, 16), 1),((22, 22), 1), ((24, 24), 1), ((21, 22), 1), ((20, 20), 1), ((21, 20), 1), ((24, 21), 1), ((24, 22), 1),((23, 22), 1), ((20, 23), 1))  # Score(score=188.212, size=211, time=0.892))
    initial_board = (((19, 21), 1), ((22, 21), 1), ((22, 22), 1), ((18, 21), 1), ((19, 19), 1), ((19, 18), 1), ((18, 19), 1), ((20, 21), 1), ((22, 20), 1), ((19, 20), 1)) # Score(score=222.851, size=223, time=0.999))
    #initial_board = (((18, 18), 1), ((17, 18), 1), ((16, 19), 1), ((16, 17), 1), ((22, 16), 1), ((20, 19), 1), ((24, 17), 1), ((23, 17), 1), ((21, 17), 1), ((23, 16), 1), ((21, 19), 1), ((20, 18), 1), ((19, 20), 1), ((17, 22), 1),((18, 22), 1), ((22, 21), 1), ((23, 22), 1), ((20, 21), 1), ((21, 21), 1),((23, 21), 1))  # Score(score=196.232, size=228, time=0.8606666666666667))
    #initial_board = (((17, 17), 1), ((16, 16), 1), ((18, 16), 1), ((19, 19), 1), ((18, 17), 1), ((22, 16), 1), ((23, 18), 1), ((21, 19), 1), ((24, 16), 1), ((23, 19), 1), ((22, 17), 1), ((24, 17), 1), ((19, 20), 1), ((16, 22), 1), ((19, 24), 1), ((17, 21), 1), ((24, 20), 1), ((22, 22), 1), ((20, 22), 1), ((20, 23), 1), ((20, 21), 1), ((24, 18), 1)) # Score(score=235.84266666666664, size=236, time=0.9993333333333333)) # Iteration 2056!
    gui = GUI(dict(initial_board), 40)
    gui.start()


if __name__ == '__main__':
    main()
