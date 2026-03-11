#!/usr/bin/env python3
"""Earley parser — general context-free grammar parsing. Zero deps."""

class Rule:
    def __init__(self, lhs, rhs): self.lhs=lhs; self.rhs=tuple(rhs)
    def __repr__(self): return f"{self.lhs} → {' '.join(self.rhs)}"

class State:
    def __init__(self, rule, dot=0, origin=0):
        self.rule=rule; self.dot=dot; self.origin=origin
    def complete(self): return self.dot >= len(self.rule.rhs)
    def next_sym(self): return self.rule.rhs[self.dot] if not self.complete() else None
    def __eq__(self, o): return self.rule==o.rule and self.dot==o.dot and self.origin==o.origin
    def __hash__(self): return hash((id(self.rule), self.dot, self.origin))

def earley_parse(grammar, start, tokens):
    chart = [set() for _ in range(len(tokens)+1)]
    for r in grammar:
        if r.lhs == start: chart[0].add(State(r, 0, 0))
    for i in range(len(tokens)+1):
        queue = list(chart[i])
        seen = set(chart[i])
        while queue:
            state = queue.pop(0)
            if state.complete():  # Completer
                for s in list(chart[state.origin]):
                    if not s.complete() and s.next_sym() == state.rule.lhs:
                        ns = State(s.rule, s.dot+1, s.origin)
                        if ns not in seen: seen.add(ns); chart[i].add(ns); queue.append(ns)
            elif state.next_sym().isupper():  # Predictor (non-terminal)
                for r in grammar:
                    if r.lhs == state.next_sym():
                        ns = State(r, 0, i)
                        if ns not in seen: seen.add(ns); chart[i].add(ns); queue.append(ns)
            elif i < len(tokens) and tokens[i] == state.next_sym():  # Scanner
                ns = State(state.rule, state.dot+1, state.origin)
                chart[i+1].add(ns)
    return any(s.complete() and s.rule.lhs==start and s.origin==0 for s in chart[len(tokens)])

def test():
    # S → S + S | S * S | n
    grammar = [Rule("S",["S","+","S"]), Rule("S",["S","*","S"]), Rule("S",["n"])]
    assert earley_parse(grammar, "S", ["n","+","n","*","n"])
    assert earley_parse(grammar, "S", ["n"])
    assert not earley_parse(grammar, "S", ["+","n"])
    assert not earley_parse(grammar, "S", [])
    print("Earley parser tests passed!")

if __name__ == "__main__": test()
