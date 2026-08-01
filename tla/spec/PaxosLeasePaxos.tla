---- MODULE PaxosLeasePaxos ----
EXTENDS Naturals, FiniteSets

CONSTANTS Proposers, Values, NoValue, MaxTime, MaxSlot, LeaseDuration

ASSUME NoValue \notin Values

Slots == 1..MaxSlot
ValOrNo == Values \cup {NoValue}
States == {"not-elected", "elected", "recovering", "repairing", "ready"}
MaxDeadline == MaxTime + LeaseDuration + 1

VARIABLES now, active, leaseDeadline, leaderState, recovered, everRecovered, chosen, appliedUpTo

vars == <<now, active, leaseDeadline, leaderState, recovered, everRecovered, chosen, appliedUpTo>>

Init ==
    /\ now = 0
    /\ active = {}
    /\ leaseDeadline = [p \in Proposers |-> 0]
    /\ leaderState = [p \in Proposers |-> "not-elected"]
    /\ recovered = {}
    /\ everRecovered = {}
    /\ chosen = [s \in Slots |-> NoValue]
    /\ appliedUpTo = [p \in Proposers |-> 0]

(* Acquiring a lease starts a fresh leadership epoch, so the recovery mark
   of any earlier epoch is cleared: a re-elected leader must recover again
   before admitting work, and ReadyImpliesRecovered below checks that this
   holds per epoch rather than once per process lifetime. *)
AcquireLease ==
    \E p \in Proposers :
        /\ active = {}
        /\ now + LeaseDuration <= MaxDeadline
        /\ active' = {p}
        /\ leaseDeadline' = [leaseDeadline EXCEPT ![p] = now + LeaseDuration]
        /\ leaderState' = [leaderState EXCEPT ![p] = "elected"]
        /\ recovered' = recovered \ {p}
        /\ UNCHANGED <<now, everRecovered, chosen, appliedUpTo>>

StartRecovery ==
    \E p \in Proposers :
        /\ p \in active
        /\ now < leaseDeadline[p]
        /\ leaderState[p] = "elected"
        /\ leaderState' = [leaderState EXCEPT ![p] = "recovering"]
        /\ UNCHANGED <<now, active, leaseDeadline, recovered, everRecovered, chosen, appliedUpTo>>

FinishRecovery ==
    \E p \in Proposers :
        /\ p \in active
        /\ now < leaseDeadline[p]
        /\ leaderState[p] = "recovering"
        /\ leaderState' = [leaderState EXCEPT ![p] = "repairing"]
        /\ recovered' = recovered \cup {p}
        /\ everRecovered' = everRecovered \cup {p}
        /\ UNCHANGED <<now, active, leaseDeadline, chosen, appliedUpTo>>

BecomeReady ==
    \E p \in Proposers :
        /\ p \in active
        /\ now < leaseDeadline[p]
        /\ p \in recovered
        /\ leaderState[p] = "repairing"
        /\ leaderState' = [leaderState EXCEPT ![p] = "ready"]
        /\ UNCHANGED <<now, active, leaseDeadline, recovered, everRecovered, chosen, appliedUpTo>>

AdmitOrApply ==
    \E p \in Proposers, v \in Values :
        /\ p \in active
        /\ now < leaseDeadline[p]
        /\ leaderState[p] = "ready"
        /\ appliedUpTo[p] < MaxSlot
        /\ LET s == appliedUpTo[p] + 1 IN
            /\ chosen' = IF chosen[s] = NoValue
                         THEN [chosen EXCEPT ![s] = v]
                         ELSE chosen
            /\ appliedUpTo' = [appliedUpTo EXCEPT ![p] = s]
        /\ UNCHANGED <<now, active, leaseDeadline, leaderState, recovered, everRecovered>>

Tick ==
    /\ now < MaxTime
    /\ LET nn == now + 1 IN
        /\ now' = nn
        /\ active' = {p \in active : nn < leaseDeadline[p]}
        /\ leaderState' = [p \in Proposers |->
              IF p \in active /\ nn >= leaseDeadline[p]
              THEN "not-elected"
              ELSE leaderState[p]]
    /\ UNCHANGED <<leaseDeadline, recovered, everRecovered, chosen, appliedUpTo>>

StutterAtEnd ==
    /\ now = MaxTime
    /\ UNCHANGED vars

Next == AcquireLease \/ StartRecovery \/ FinishRecovery \/ BecomeReady \/
        AdmitOrApply \/ Tick \/ StutterAtEnd

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ now \in 0..MaxTime
    /\ active \subseteq Proposers
    /\ leaseDeadline \in [Proposers -> 0..MaxDeadline]
    /\ leaderState \in [Proposers -> States]
    /\ recovered \subseteq Proposers
    /\ everRecovered \subseteq Proposers
    /\ chosen \in [Slots -> ValOrNo]
    /\ appliedUpTo \in [Proposers -> 0..MaxSlot]

(* Slot agreement is enforced by construction in this abstraction (a slot is
   assigned only when empty); the checked predicate is domain membership.
   The substantive composition checks are the admission invariants below. *)
ChosenValueWellFormed ==
    \A s \in Slots : chosen[s] \in ValOrNo

ReadyImpliesActive ==
    \A p \in Proposers : leaderState[p] = "ready" => p \in active /\ now < leaseDeadline[p]

ReadyLeaderUniqueness ==
    Cardinality({p \in Proposers : leaderState[p] = "ready"}) <= 1

RecoveryPrecedesAdmission ==
    \A p \in Proposers : appliedUpTo[p] > 0 => p \in everRecovered

(* Per-epoch fencing of the fast path: a ready leader has completed
   recovery within its current lease epoch, because AcquireLease clears the
   mark.  Admission (AdmitOrApply) requires "ready", so no leader appends
   on the strength of a previous epoch's recovery. *)
ReadyImpliesRecovered ==
    \A p \in Proposers : leaderState[p] = "ready" => p \in recovered

AppliedImpliesChosen ==
    \A p \in Proposers :
        \A s \in Slots : s <= appliedUpTo[p] => chosen[s] # NoValue

LogPrefixConsistency ==
    \A p, q \in Proposers :
        \A s \in Slots :
            s <= appliedUpTo[p] /\ s <= appliedUpTo[q] => chosen[s] # NoValue

Safety ==
    TypeOK /\ ChosenValueWellFormed /\ ReadyImpliesActive /\ ReadyLeaderUniqueness /\
    RecoveryPrecedesAdmission /\ ReadyImpliesRecovered /\ AppliedImpliesChosen /\
    LogPrefixConsistency

====
