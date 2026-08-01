---- MODULE PaxosLeaseProof ----
EXTENDS Naturals

(***************************************************************************)
(* TLAPS status for the artifact.  These are the arithmetic lemmas used by  *)
(* the timing argument: timer containment, the quarantine bound and its     *)
(* tightness, deadline capping, and the clock-rate condition.  They are     *)
(* not a complete parameterized proof of the executable transition          *)
(* relation in spec/PaxosLease.tla.                                         *)
(***************************************************************************)

(* If the proposer starts its timer no later than each certificate acceptor
   starts its exclusion, and its duration is no longer, the proposer's
   authority interval is contained in the acceptor's exclusion interval. *)
THEOREM TimerContainmentArithmetic ==
    \A startP, startA, durP, durA \in Nat :
        startP <= startA /\ durP <= durA => startP + durP <= startA + durA
  OBVIOUS

(* The quarantine bound.  Everything an acceptor can forget -- a promise or
   an accepted lease -- belongs to a proposer attempt whose Prepare was sent
   at some tPrep no later than the crash (the promise was given to that
   attempt; the accepted lease was accepted by it).  Under the prepare-time
   timer rule the attempt is unusable after tPrep + durP.  Quarantine at
   least the proposer duration therefore outlasts every attempt that any
   forgotten fact could still support.  Note the dependence on the timer
   rule: with the step-3 rule of the 2012 paper there is no tPrep + durP
   bound, and no finite quarantine suffices
   (counterexamples/LateTimer.tla). *)
THEOREM QuarantineCoversForgottenFacts ==
    \A tPrep, tCrash, tRestart, durP, q \in Nat :
        tPrep <= tCrash /\ tCrash <= tRestart /\ durP <= q
            => tPrep + durP <= tRestart + q
  OBVIOUS

(* The quarantine bound for the implemented protocol
   (spec/PaxosLeaseImpl.tla): lease timer at prepare-quorum receipt, attempt
   timeout of durR armed at Prepare, timely timeout dispatch.  Everything an
   acceptor can forget again belongs to an attempt whose Prepare preceded
   the crash, but the attempt's lifetime now has two components and the
   quarantine must cover whichever applies.  A forgotten promise can
   support an activation only while the attempt is current, i.e. before
   tPrep + durR (the timeout abandons the ballot and the identifier check
   discards its responses).  A forgotten accepted lease was accepted after
   the proposer's timer started at some tQuorum <= tCrash, and that
   authority ends at tQuorum + durP.  Quarantine at least
   max(durP, durR) therefore covers both cases; TLC confirms the bound is
   tight in both coordinates (PaxosLeaseImplTimely{Boundary,Below,
   RDominant,RDominantSafe}.cfg).  Under delayed dispatch the durR bound
   does not exist and no inequality between the shipped constants helps
   (PaxosLeaseImplDelayedShipped.cfg). *)
THEOREM ImplQuarantineCoversForgottenFacts ==
    \A tPrep, tQuorum, tCrash, tRestart, durP, durR, q \in Nat :
        /\ tPrep <= tCrash
        /\ tQuorum <= tCrash
        /\ tCrash <= tRestart
        /\ durR <= q
        /\ durP <= q
        => /\ tPrep + durR <= tRestart + q
           /\ tQuorum + durP <= tRestart + q
  OBVIOUS

(* Deadline capping in the finite model preserves containment. *)
Cap(t, m) == IF t > m THEN m ELSE t

THEOREM CapMonotone ==
    \A x, y, m \in Nat : x <= y => Cap(x, m) <= Cap(y, m)
  BY DEF Cap

(* The quarantine bound is necessary: any quarantine strictly below the
   proposer duration leaves an elapsed interval inside a forgotten
   attempt's lifetime but outside quarantine.  TLC turns this arithmetic
   gap into concrete two-owner executions
   (spec/PaxosLeaseUnsafeQuarantine.cfg). *)
THEOREM QuarantineBoundTight ==
    \A q, durP \in Nat : q < durP => \E e \in Nat : e <= durP /\ ~(e <= q)
  OBVIOUS

(* The clock-rate condition.  If the proposer's clock runs at rate at least
   rMin (so local reading dP has not elapsed before real time realP with
   rMin * realP <= dP), the acceptor's clock runs at rate at most rMax (so
   local dA has elapsed by real time realA with dA <= rMax * realA), then
   choosing durations with dP * rMax <= dA * rMin gives real-time
   containment: realP <= realA.  The same arithmetic, with the quarantine
   in place of dA, gives the real-time quarantine bound used by the Python
   timing module. *)
THEOREM DriftContainmentArithmetic ==
    \A realP, realA, dP, dA, rMin, rMax \in Nat :
        /\ rMin > 0
        /\ rMax > 0
        /\ rMin * realP <= dP
        /\ dA <= rMax * realA
        /\ dP * rMax <= dA * rMin
        => realP <= realA
  PROOF
    <1> SUFFICES ASSUME NEW realP \in Nat, NEW realA \in Nat,
                        NEW dP \in Nat, NEW dA \in Nat,
                        NEW rMin \in Nat, NEW rMax \in Nat,
                        rMin > 0, rMax > 0,
                        rMin * realP <= dP,
                        dA <= rMax * realA,
                        dP * rMax <= dA * rMin
                 PROVE realP <= realA
      OBVIOUS
    <1>1. (rMin * realP) * rMax <= dP * rMax
      OBVIOUS
    <1>2. dA * rMin <= (rMax * realA) * rMin
      OBVIOUS
    <1>3. (rMin * rMax) * realP <= (rMin * rMax) * realA
      BY <1>1, <1>2
    <1>4. rMin * rMax > 0
      OBVIOUS
    <1> QED
      BY <1>3, <1>4
====
