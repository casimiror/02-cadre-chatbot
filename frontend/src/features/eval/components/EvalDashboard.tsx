import { useEvalSection } from "../hooks/useEvalSection";
import type { AnswerRun, RetrievalRun } from "../types";
import { AnswerSection } from "./AnswerSection";
import { RetrievalSection } from "./RetrievalSection";

// Container: one hook per section; only one evaluation runs at a time.
export function EvalDashboard() {
  const retrieval = useEvalSection<RetrievalRun>("retrieval");
  const answer = useEvalSection<AnswerRun>("answer");
  const busy = Boolean(retrieval.job || answer.job);

  return (
    <div className="eval">
      <header className="eval__header">
        <h1>Evaluation</h1>
        <p>
          The support agent on the 60-case dataset: the knowledge-base retrieval (RAG) and the agent's answers (LLM),
          evaluated separately. Results are saved per run and sent to Langfuse.
        </p>
      </header>
      {retrieval.disabled ? (
        <p className="eval__notice">
          Evaluation is turned off here. Run the app locally with <code>EVAL_ENABLED=true</code> in <code>.env</code>.
        </p>
      ) : retrieval.loading ? (
        <p className="eval__notice">Loading the latest runs…</p>
      ) : (
        <>
          <RetrievalSection state={retrieval} busy={busy} />
          <AnswerSection state={answer} busy={busy} />
        </>
      )}
    </div>
  );
}
