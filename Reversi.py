convert = lambda x: (int(x[1]) - 1, ord(x[0].lower()) - 97)
ERROR = ('E', None, None, None, None)
def can_move(B, W, T):
    Q = set(B + W)
    for i in range(8):
        for j in range(8):
            if (i, j) not in Q:
                try:
                    fmove(i, j, B, W, T)
                    return True
                except:
                    pass
    return False
def play(moves):
    try:
        moves = [*map(convert, [moves[i:i+2] for i in range(0, len(moves), 2)])]
        if len(moves) != len(set(moves)):
            return ERROR
    except:
        return ERROR
    W, B, T = [(3, 3), (4, 4)], [(3, 4), (4, 3)], 0
    for my, mx in moves:
        try:
            B, W = fmove(my, mx, B, W, T)
            T = (T + 1) % 2
        except:
            if can_move(B[:], W[:] ,T):
                return ERROR
            try:
                B,W = fmove(my, mx, B, W, (T+1)%2)
            except:
                return ERROR
    is_complete = True
    turn = None
    if can_move(B[:], W[:], T):
        is_complete = False
        turn = 'B' if T == 0 else 'W'

    elif can_move(B[:], W[:], (T + 1) % 2):
        is_complete = False
        turn = 'W' if (T + 1) % 2 else 'B'

    state = 'C' if is_complete else 'I'
    if state == 'C':
        if len(B) > len(W):
            winner = 'B'
        elif len(W) > len(B):
            winner = 'W'
        else:
            winner = 'D'
    else:
        winner = 'I'
    Bl = len(B)
    Wl = len(W)
    if winner != 'I':
        if winner == 'D':
            Bl = 32
            Wl = 32
        elif winner == 'W':
            Wl = 64 - Bl
        else:
            Bl = 64 - Wl
    return (state, turn, winner, Bl, Wl)

def fmove(my, mx, B, W, T):
    side = B if not T else W
    other = B if T else W
    bag = []
    #Changed this
    def D(y, x):
        a = (y - my)
        b = (x - mx)
        return (a if a > 0 else -a) + (b if b > 0 else -b)
    in_cover = lambda y, x: y == my or x == mx or y + x == my + mx or y - x == my - mx
    dir_of_m = lambda y, x: (0 if y == my else -1 if y > my else 1, 0 if x == mx else -1 if x > mx else 1)
    for y, x in side:
        if in_cover(y, x):  
            current = []
            if any(D(y_, x_) < D(y, x) and dir_of_m(y_, x_) == dir_of_m(y, x)
                    and in_cover(y_, x_) for y_, x_ in side):
                continue
            else:
                dy, dx = (0 if y == my else -1 if y > my else 1, 0 if x == mx else -1 if x > mx else 1)
                c = 0
                while (y, x) != (my, mx):
                    c += 1
                    y += dy
                    x += dx
                    if (y, x) in other:
                        current.append((y, x))
                if c == len(current) + 1:
                    bag += current
    if not bag:
        raise ValueError()
    else:
        for y, x in bag:
            other.remove((y, x))
            side.append((y, x))
    side.append((my,mx))
    return (side if not T else other, side if T else other)

class ReversiBoard(object):
    @classmethod
    def interpret_transcript(cls, move_str):
        return play(move_str)
