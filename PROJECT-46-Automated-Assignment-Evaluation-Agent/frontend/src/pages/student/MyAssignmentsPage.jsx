import React, { useState, useEffect } from 'react';
import { BookOpen, Calendar, UploadCloud, FileText, CheckCircle2, Sliders, AlertCircle } from 'lucide-react';
import { assignmentService } from '../../services/assignmentService';
import { submissionService } from '../../services/submissionService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { Loader } from '../../components/common/Loader';
import { formatDate } from '../../utils/formatters';

export const MyAssignmentsPage = () => {
  const [assignments, setAssignments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const toast = useToast();

  const loadAssignments = async () => {
    try {
      const data = await assignmentService.listAssignments();
      setAssignments(data);
    } catch (err) {
      toast.error('Failed to load assignments.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAssignments();
  }, []);

  const handleOpenSubmit = (assignment) => {
    setSelectedAssignment(assignment);
    setFile(null);
    setIsSubmitModalOpen(true);
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file || !selectedAssignment) {
      toast.error('Please select a file to submit.');
      return;
    }

    setIsUploading(true);
    try {
      const res = await submissionService.uploadSubmission(selectedAssignment.id, file);
      toast.success(`Submission '${res.file_name}' uploaded successfully (${res.word_count} words extracted)!`);
      setIsSubmitModalOpen(false);
      setFile(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Submission failed.');
    } finally {
      setIsUploading(false);
    }
  };

  if (isLoading) {
    return <Loader message="Loading your course assignments..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Course Assignments</h1>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          Select an assignment to read the problem brief and submit your solution document.
        </p>
      </div>

      {assignments.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: '3rem' }}>
          <BookOpen size={40} color="var(--primary-500)" style={{ margin: '0 auto 0.75rem' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>No active assignments</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.3rem' }}>
            Check back once your instructor publishes a new assignment!
          </p>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
          {assignments.map((a) => {
            const rubric = a.rubrics?.[0];
            return (
              <Card
                key={a.id}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    {a.code && (
                      <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: 'rgba(79, 70, 229, 0.08)', color: 'var(--primary-500)' }}>
                        {a.code}
                      </span>
                    )}
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Max {a.max_score} pts
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                    {a.title}
                  </h3>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '1rem', whiteSpace: 'pre-wrap', maxHeight: '100px', overflowY: 'auto' }}>
                    {a.instructions || a.description}
                  </p>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    <Calendar size={14} />
                    <span>Due: {formatDate(a.due_date)}</span>
                  </div>

                  {/* Rubric criteria mini-chips */}
                  {rubric?.criteria && (
                    <div style={{ marginBottom: '1.25rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Graded Criteria:
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.35rem' }}>
                        {rubric.criteria.map((c) => (
                          <span
                            key={c.id}
                            style={{
                              fontSize: '0.725rem',
                              padding: '3px 8px',
                              borderRadius: '4px',
                              backgroundColor: '#f1f5f9',
                              color: 'var(--text-secondary)',
                              fontWeight: 500,
                            }}
                          >
                            {c.name} ({c.max_points}p)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                  <Button
                    variant="primary"
                    icon={UploadCloud}
                    onClick={() => handleOpenSubmit(a)}
                    style={{ width: '100%' }}
                  >
                    Submit Assignment Document
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Submit Assignment Modal */}
      <Modal
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        title={`Submit Solution: ${selectedAssignment?.title || ''}`}
        footer={
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Button variant="secondary" onClick={() => setIsSubmitModalOpen(false)} disabled={isUploading}>
              Cancel
            </Button>
            <Button variant="primary" icon={UploadCloud} onClick={handleUploadSubmit} isLoading={isUploading}>
              Upload & Submit
            </Button>
          </div>
        }
      >
        <form onSubmit={handleUploadSubmit}>
          <div
            style={{
              border: '2px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '2rem 1.5rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              marginBottom: '1rem',
            }}
          >
            <UploadCloud size={40} color="var(--primary-500)" style={{ margin: '0 auto 0.75rem' }} />
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Select Submission File</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem', marginBottom: '1rem' }}>
              Accepted formats: PDF (.pdf), Microsoft Word (.docx), Plain Text (.txt), Code files (.py, .java, .js, .cpp)
            </p>

            <input
              type="file"
              id="student-file-upload"
              style={{ display: 'none' }}
              accept=".pdf,.docx,.txt,.md,.py,.java,.cpp,.c,.js"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                }
              }}
            />
            <label htmlFor="student-file-upload">
              <span className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                Browse Computer
              </span>
            </label>

            {file && (
              <div style={{ marginTop: '1rem', padding: '8px 12px', borderRadius: 'var(--radius-md)', background: 'rgba(79, 70, 229, 0.08)', color: 'var(--primary-500)', fontSize: '0.85rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.4rem', border: '1px solid rgba(79, 70, 229, 0.2)' }}>
                <FileText size={16} />
                <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>
        </form>
      </Modal>
    </div>
  );
};
