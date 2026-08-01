---- MODULE PaxosLeaseSym ----
EXTENDS PaxosLease, TLC
Symm == Permutations(Proposers) \cup Permutations(Acceptors)
====
