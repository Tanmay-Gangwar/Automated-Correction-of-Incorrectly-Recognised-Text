from queue import PriorityQueue

class SentenceCorrector(object):
    def __init__(self, cost_fn, conf_matrix):
        self.conf_matrix = {}
        for key in conf_matrix:
            for c in conf_matrix[key]:
                if c not in self.conf_matrix: self.conf_matrix[c] = []
                self.conf_matrix[c].append(key)
        self.cost_fn = cost_fn
        self.best_cost = float('inf')

        # You should keep updating following variable with best string so far.
        self.best_state = None  


    def search(self, start_state):
        self.best_state = start_state
        self.best_cost = self.cost_fn(start_state)
        self.bigThenSmall(start_state)
        self.onlySmall(start_state)
        self.onlySmall(self.best_state)
        cnt = 100
        while True:
            self.hillClimbWords(start_state, start_state, cnt)
            cnt *= 4
    

    def bigThenSmall(self, start_state):
        startParts = start_state.split(" ")
        start_state = self.hillClimb(start_state, start_state)
        if self.cost_fn(start_state) < self.cost_fn(self.best_state):
            self.best_state = start_state
        for i in range(len(startParts)-2):
            parts = self.best_state.split(" ")
            state = "{} {} {}".format(parts[i], parts[i + 1], parts[i + 2])
            startState = "{} {} {}".format(startParts[i], startParts[i + 1], startParts[i + 2])
            state = self.hillClimbSmall(state, startState)
            state = state.split(" ")
            parts[i] = state[0]
            parts[i + 1] = state[1]
            parts[i + 2] = state[2]
            state = " ".join(parts)
            if self.cost_fn(state) < self.cost_fn(self.best_state):
                self.best_state = state


    def onlySmall(self, start_state):
        parts = start_state.split(" ")
        for i in range(len(parts)-2):
            state = "{} {} {}".format(parts[i], parts[i + 1], parts[i + 2])
            state = self.hillClimbSmall(state, state)
            state = state.split(" ")
            parts[i] = state[0]
            parts[i + 1] = state[1]
            parts[i + 2] = state[2]
            state = " ".join(parts)
            if state != self.best_state and self.cost_fn(state) < self.cost_fn(self.best_state):
                self.best_state = state


    def hillClimbSmall(self, state, start_state):
        bestState = state
        bestCost = self.cost_fn(state)
        for i in range(len(state)):
            if start_state[i] not in self.conf_matrix: continue
            for j in range(i, len(state)):
                if start_state[j] not in self.conf_matrix: continue
                orig = state
                for c1 in self.conf_matrix[start_state[i]]:
                    for c2 in self.conf_matrix[start_state[j]]:
                        state = state[:i] + c1 + state[i + 1:]
                        state = state[:j] + c2 + state[j + 1:]
                        cost = self.cost_fn(state)
                        if cost < bestCost:
                            bestCost = cost
                            bestState = state
                        state = orig
        
        if bestState == state: return bestState
        return self.hillClimbSmall(bestState, start_state)
    

    def hillClimb(self, state, start_state):
        bestState = state
        bestCost = self.cost_fn(state)
        for i in range(len(state)):
            if start_state[i] in self.conf_matrix:
                orig = state
                for c in self.conf_matrix[start_state[i]]:
                    state = state[:i] + c + state[i+1:]
                    cost = self.cost_fn(state)
                    if cost < bestCost:
                        bestCost = cost
                        bestState = state
                    state = orig
        if bestState == state: return bestState
        return self.hillClimb(bestState, start_state)
    

    def hillClimbWords(self, state, start, cnt):
        words = state.split(' ')
        startWords = start.split(' ')
        bestCost = self.cost_fn(state)
        changed = True
        wordMap = [self.hillClimbForWord(word, start, cnt) for word, start in zip(words, startWords)]
        while changed:
            changed = False
            changedWord = None
            for i in range(len(words)):
                orig = words[i]
                for word in wordMap[i]:
                    words[i] = word
                    tempState = ' '.join(words)
                    cost = self.cost_fn(tempState)
                    if cost < self.best_cost: 
                        self.best_state = tempState
                        self.best_cost = cost
                    if cost < bestCost:
                        bestCost = cost
                        changedWord = (i, word)
                        changed = True
                words[i] = orig
            if changedWord:
                i, word = changedWord
                words[i] = word
            
        
    def hillClimbForWord(self, state, start, cnt):
        pq = PriorityQueue(cnt)
        elements = set()
        orig = state
        for i in range(len(state)):
            if start[i] not in self.conf_matrix: continue
            for j in range(i, len(state)):
                if start[j] not in self.conf_matrix: continue
                for k in range(j, len(state)):
                    if start[k] not in self.conf_matrix: continue
                    for u in self.conf_matrix[start[i]]:
                        for v in self.conf_matrix[start[j]]:
                            for w in self.conf_matrix[start[k]]:
                                state = state[ : i] + u + state[i + 1 : ]
                                state = state[ : j] + v + state[j + 1 : ]
                                state = state[ : k] + w + state[k + 1 : ]
                                if state not in elements:
                                    cost = self.cost_fn(state)
                                    if pq.full():
                                        top = pq.get()
                                        topCost = -top[0]
                                        if self.cost_fn(state) < topCost: 
                                            pq.put((-cost, state))
                                            elements.remove(top[1])
                                            elements.add(state)
                                        else: pq.put(top)
                                    else: 
                                        pq.put((-cost, state))
                                        elements.add(state)
                                state = orig
        return list(elements)
