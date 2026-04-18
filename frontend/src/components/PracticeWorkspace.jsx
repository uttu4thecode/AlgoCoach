import { useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  wordWrap: 'on',
  smoothScrolling: true,
  scrollBeyondLastLine: false,
  padding: { top: 18, bottom: 18 },
};

function PracticeWorkspace({ problems = [] }) {
  const [selectedProblemId, setSelectedProblemId] = useState(problems[0]?.id || '');
  const [codeByProblem, setCodeByProblem] = useState({});

  useEffect(() => {
    if (!problems.length) {
      return;
    }

    setSelectedProblemId((current) => current || problems[0].id);
    setCodeByProblem((current) => {
      const next = { ...current };

      problems.forEach((problem) => {
        if (!(problem.id in next)) {
          next[problem.id] = problem.starterCode;
        }
      });

      return next;
    });
  }, [problems]);

  const selectedProblem = problems.find((problem) => problem.id === selectedProblemId) || problems[0];
  const currentCode = selectedProblem ? codeByProblem[selectedProblem.id] || selectedProblem.starterCode : '';

  const handleEditorChange = (value) => {
    if (!selectedProblem) {
      return;
    }

    setCodeByProblem((current) => ({
      ...current,
      [selectedProblem.id]: value ?? '',
    }));
  };

  return (
    <section className="practice-layout">
      <div className="surface-card practice-problems">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Code editor</p>
            <h2>Practice queue</h2>
          </div>
        </div>

        <div className="problem-list">
          {problems.map((problem) => {
            const isActive = problem.id === selectedProblem?.id;

            return (
              <button
                key={problem.id}
                className={`problem-card ${isActive ? 'is-active' : ''}`}
                type="button"
                onClick={() => setSelectedProblemId(problem.id)}
              >
                <span className="problem-card__meta">
                  <strong>{problem.title}</strong>
                  <span>{problem.topic}</span>
                </span>
                <span className={`difficulty-badge difficulty-${problem.difficulty.toLowerCase()}`}>
                  {problem.difficulty}
                </span>
                <p>{problem.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      <div className="surface-card practice-editor">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Live workspace</p>
            <h2>{selectedProblem?.title || 'Select a problem'}</h2>
          </div>
          <span className="pill">{selectedProblem?.topic || 'Coding'}</span>
        </div>

        <div className="editor-shell">
          <Editor
            height="460px"
            defaultLanguage="python"
            language="python"
            theme="vs-dark"
            value={currentCode}
            options={editorOptions}
            onChange={handleEditorChange}
          />
        </div>

        <div className="editor-footer">
          <div>
            <strong>Interview cue</strong>
            <p>State brute force, optimize deliberately, and narrate edge cases before coding.</p>
          </div>
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              if (!selectedProblem) {
                return;
              }

              setCodeByProblem((current) => ({
                ...current,
                [selectedProblem.id]: selectedProblem.starterCode,
              }));
            }}
          >
            Reset starter
          </button>
        </div>
      </div>
    </section>
  );
}

export default PracticeWorkspace;
