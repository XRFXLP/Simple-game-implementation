from functools import reduce
from copy import deepcopy
def neighbours(piece, board, toS = '.'):
    liberties = set()
    for i in (1, 0), (0, 1), (-1, 0), (0, -1):
        move = (i[0] + piece[0], i[1] + piece[1])
        try:
            if min(move) > -1 and board[move[0]][move[1]] == toS:
                liberties.add(move)
        except:
            pass
    return liberties

class cluster:
    def __init__(self, colour):
        self.colour = colour
        self.pieces = []
        self.liberty = set()


    def add(self, piece, board):
        r = deepcopy(self.liberty)
        self.liberty = self.liberty.union(neighbours(piece, board))
        self.liberty.discard(piece)
        self.pieces.append(piece)       
        return list(self.liberty - r)
    def __add__(self, other):
        self.liberty = self.liberty.union(other.liberty)
        self.pieces += other.pieces
        T = cluster(self.colour)
        T.liberty = self.liberty
        T.pieces = self.pieces
        return T

    def check_op(self, piece):
        discarded = []
        if piece in self.liberty:
            self.liberty.discard(piece)
            discarded.append(piece)
        return discarded

    def check_ad(self, piece):
        return piece in self.liberty

    def __eq__(self, other):
        return self.pieces == other.pieces

class Go:
    def __init__(self, h , w = None):
        w = h if not w else w
        if w > 26 or h > 26:    raise ValueError("You're not allowed to play with that big board")
        self.w = w
        self.h = h
        self.board = [['.' for i in range(w)] for i in range(h)]
        self.player = "x"
        self.alphabet = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        self.o_clusters = []
        self.x_clusters = []
        self.moves = []
        self.handiF = 0

    def move(self, *sequence):
      #  print(sequence)
        for move in sequence:
            rollB = 0
            MOVE = {}
            a, b = self.h - int(move[:-1]), self.alphabet.index(move[-1]) 

            if self.board[a][b] != '.':
                raise ValueError()

            MOVE = {'move_loc': (a, b), 'color': self.player}
            MOVE['board'] = '\n'.join([''.join(i) for i in self.board])
            self.board[a][b] = self.player

            MOVE['reductions'] = []

            opposite = self.x_clusters if self.player == 'o' else self.o_clusters
            for i in range(len(opposite)):
                k = opposite[i].check_op((a, b))
                if k:
                    MOVE['reductions'].append((opposite[i], k))

            to_be_deleted = []; MOVE['deletions'] = []
            deleted_piece = []

            for i in range(len(opposite)):
                if len(opposite[i].liberty) == 0:
                    to_be_deleted.append(i)
                    MOVE['deletions'].append(opposite[i])
                    for j in opposite[i].pieces:
                        if neighbours(j, self.board, 'x' if self.player == 'x' else 'o'):
                            deleted_piece += [(i, j) for i in neighbours(j, self.board, 'x' if self.player == 'x' else 'o')]
                        self.board[j[0]][j[1]] = '.'

            for i in to_be_deleted[::-1]:
                del opposite[i]





            player = self.x_clusters if self.player == "x" else self.o_clusters
            flag = 0; MOVE['lib_change'] = []
            possible = []
            for i in range(len(player)):
                for ll in deleted_piece:
                    if ll[0] in player[i].pieces:
                        player[i].liberty.add(ll[1])
                if player[i].check_ad((a, b)):
                    flag = 1
                    possible.append(i)
                    dis = player[i].add((a, b), self.board)
                    MOVE['lib_change'].append((player[i], (('-', (a, b)), ) + tuple([('+', k) for k in dis])))
              #  if len(player[i].liberty)  == 0:
               #     rollB = 1

            MOVE['cluster'] = None
            if flag == 0:
                new_cluster = cluster(self.player)
                new_cluster.add((a, b), self.board)
                if len(new_cluster.liberty) == 0:
                    rollB = 1
                MOVE['cluster'] = new_cluster
                player.append(new_cluster)
            MOVE['merges'] = []

            if len(possible) > 1:
                initial = [player[i] for i in possible]
                final = reduce(lambda a, b: a + b, initial)
                player[possible[0]] = final
                MOVE['merges'] = [initial, final]



            for f in possible[1:][::-1]:
                del player[f]


            #protection
            if self.player == 'x':
                self.x_clusters = player
                self.o_clusters = opposite
            else:
                self.o_clusters = player
                self.x_clusters = opposite
           print(rollB)
           if move:
               print("The game and move was", move)
               print("________________________v_____________________")
               print("   " + " ".join("ABCDEFGHJKLMNOPQRSTUVWXYZ"[:self.w]))
               print("\n".join([str(self.h - j).zfill(2) + " " + ' '.join(i) for j, i in enumerate(self.board)]))
               print("\n\n")
               print("________________________^______________________")
            
            if len(self.moves) > 2 and 'board' in self.moves[-1] and self.moves[-1]['board'] == '\n'.join([''.join(i) for i in self.board]):
                rollB = 1

            self.moves.append(MOVE)
            if rollB:
                self.rollback(1, 1)
                raise ValueError()

            self.player = 'x' if self.player == 'o' else  'o'
        return self.board

    def get_position(self, st):
        l = self.alphabet.index(st[-1]) 
        n = self.w - int(st[:-1]) 
        return self.board[n][l]

    def handicap_stones(self, n):
        print("Yes handicapping",n)
        handi = {9: [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)],
                13: [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)],
                19: [(3, 15), (15, 3), (15, 15), (3, 3),(9, 9), (9, 3), (9, 15), (3, 9), (15, 9)]
                }
        if self.h == self.h and self.h not in handi or n > len(handi[self.h]) or self.handiF == 1 or self.moves:
            raise ValueError()
        for pos in handi[self.h][:n]:
            self.board[pos[0]][pos[1]] = 'x'
        self.last = 'o'
        self.handiF = 1

    @property
    def turn(self):
        return "black" if self.player == 'x' else "white"
    def pass_turn(self):
        print("turn was passed")
        self.moves.append({})
        self.player = "x" if self.player == "o" else "o"
    def reset(self):
        print("Resetted")
        self.board = [['.']*self.w for i in range(self.h)]
        self.last = None
        self.moves = []
        self.handiF = 0
        self.player = 'x'
    @property
    def size(self):
        return {"height":self.h, "width": self.w}
        
    def rollback(self, x, flag = 0):
        print("Rollbacks were done", x, flag)
        if x > len(self.moves):
            raise ValueError()
        for i in range(x):
            MOVE = self.moves.pop()
            if not MOVE:
                self.player = 'x' if self.player == 'o' else 'o'
                continue 
            self.board = [list(i) for i in MOVE['board'].split("\n")]
            player = self.x_clusters if self.player == ('o' if not flag else 'x') else self.o_clusters
            if MOVE['cluster']:
                player.remove(MOVE['cluster'])
            if MOVE['merges']:
                player.remove(MOVE['merges'][1])
                player += MOVE['merges'][0]
            opposite = self.o_clusters if self.player == ('o' if not flag else 'x') else self.x_clusters

            if MOVE['deletions']:
                opposite += MOVE['deletions']


            for k in MOVE['reductions']:
                for _ in k[1]:
                    opposite[opposite.index(k[0])].liberty.add(_)

            for l in MOVE['lib_change']:
        #        print(MOVE['lib_change'])
                ff = player.index(l[0])
                player[ff].pieces.append(MOVE['move_loc'])

                for p in l[1]:
                    if p[0] == '-':
                        player[ff].liberty.add(p[1])
                    else:
                        player[ff].liberty.discard(p[1])
            if flag == 1:
                if self.player == 'x':
                    self.x_clusters = player
                    self.o_clusters = opposite
                else:
                    self.x_clusters = opposite
                    self.o_clusters = player
            else:
                if self.player == 'o':
                    self.x_clusters = player
                    self.o_clusters = opposite
                    self.player = 'x'
                else:
                    self.x_clusters = opposite
                    self.o_clusters = player
