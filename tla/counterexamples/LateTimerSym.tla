---- MODULE LateTimerSym ----
EXTENDS LateTimer, TLC
Symm == Permutations(Proposers) \cup Permutations(Acceptors)
====
