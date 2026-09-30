import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  Sparkles,
  Award,
  Filter,
  CheckCircle2,
  AlertCircle,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { submissionService } from '../../services/submissionService';
import { assignmentService } from '../../services/assignmentService';
import { studentService } from '../../services/studentService';
import { evaluationService } from '../../services/evaluationService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loader } from '../../components/common/Loader';
import { formatDate } from '../../utils/formatters';
import { getStatusBadge } from '../../utils/statusBadges';

export const SubmissionsPage = () => {
  const [submissions, setSubmissions] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [evaluatingSubId, setEvaluatingSubId] = useState(null);

  // Upload Modal State
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadAssignId, setUploadAssignId] = useState('');
  const [uploadStudentId, setUploadStudentId] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const [subs, assigns, stus] = await Promise.all([
        submissionService.listSubmissions({
          assignmentId: selectedAssignment || null,
          status: selectedStatus || null,
        }),
        assignmentService.listAssignments(),
        studentService.listStudents(),
      ]);
      setSubmissions(subs);
      setAssignments(assigns);
      setStudents(stus);
    } catch (err) {
      toast.error('Failed to load submissions.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedAssignment, selectedStatus]);

  const handleStartEvaluation = async (submissionId) => {
    setEvaluatingSubId(submissionId);
    try {
      toast.info('Initiating Multi-Agent AI evaluation pipeline...');
      await evaluationService.startEvaluation(submissionId);
      toast.success('Evaluation complete! Result is ready for teacher review.');
      await loadData();
      navigate(`/teacher/evaluations/${submissionId}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Evaluation failed.');
    } finally {
      setEvaluatingSubId(null);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadAssignId || !uploadFile) {
      toast.error('Please choose an assignment and select a file.');
      return;
    }

    setIsUploading(true);
    try {
      const result = await submissionService.uploadSubmission(
        uploadAssignId,
        uploadFile,
        uploadStudentId || null
      );
      toast.success(`Submission '${result.file_name}' uploaded and text extracted (${result.word_count} words)!`);
      setIsUploadOpen(false);
      setUploadFile(null);
      await loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  if (isLoading) {
    return <Loader message="Loading submissions pool..." size="lg" />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Student Submissions</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            View extracted text, initiate AI agent evaluations, and inspect similarity indicators.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Button variant="secondary" icon={RefreshCw} onClick={loadData}>
            Refresh
          </Button>
          <Button variant="primary" icon={UploadCloud} onClick={() => setIsUploadOpen(true)}>
            Upload Submission
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          alignItems: 'center',
          flexWrap: 'wrap',
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <Filter size={16} /> Filter by:
        </div>

        <select
          className="form-select"
          value={selectedAssignment}
          onChange={(e) => setSelectedAssignment(e.target.value)}
          style={{ width: 'auto', minWidth: '220px' }}
        >
          <option value="">All Assignments</option>
          {assignments.map((a) => (
            <option key={a.id} value={a.id}>
              {a.title}
            </option>
          ))}
        </select>

        <select
          className="form-select"
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          style={{ width: 'auto', minWidth: '180px' }}
        >
          <option value="">All Statuses</option>
          <option value="extracted">Ready for Eval</option>
          <option value="evaluating">Evaluating</option>
          <option value="under_review">Under Review</option>
          <option value="approved">Approved</option>
          <option value="published">Published</option>
        </select>
      </div>

      {/* Submissions Table */}
      <Card>
        {submissions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <FileText size={40} color="var(--primary-500)" style={{ margin: '0 auto 0.75rem' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>No submissions found</h3>
            <p style={{ marginTop: '0.2rem', marginBottom: '1.25rem' }}>
              Try adjusting filters or upload a student submission to test the AI pipeline.
            </p>
            <Button variant="primary" icon={UploadCloud} onClick={() => setIsUploadOpen(true)}>
              Upload Submission
            </Button>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Assignment</th>
                  <th>Submitted Document</th>
                  <th>Status</th>
                  <th>AI Score</th>
                  <th>Originality</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => {
                  const statusBadge = getStatusBadge(sub.status);
                  return (
                    <tr key={sub.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{sub.student?.full_name || `Student #${sub.student_id}`}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub.student?.email}</div>
                      </td>
                      <td style={{ color: 'var(--text-secondary)' }}>
                        {sub.assignment_id ? (
                          assignments.find((a) => a.id === sub.assignment_id)?.title || `Assignment #${sub.assignment_id}`
                        ) : '—'}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          <FileText size={15} color="var(--primary-500)" />
                          {sub.file_name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {sub.word_count} words • {formatDate(sub.submitted_at)}
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${statusBadge.className}`}>{statusBadge.label}</span>
                      </td>
                      <td>
                        {sub.total_score !== null && sub.total_score !== undefined ? (
                          <strong style={{ color: 'var(--text-primary)' }}>
                            {sub.total_score} / {sub.max_possible_score || 100}
                          </strong>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>
                        {sub.similarity_percentage !== null && sub.similarity_percentage !== undefined ? (
                          <span style={{ fontWeight: 600, color: sub.similarity_percentage > 40 ? 'var(--danger)' : 'var(--success)' }}>
                            {sub.similarity_percentage}%
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          {sub.status === 'extracted' || sub.status === 'pending' ? (
                            <Button
                              size="sm"
                              variant="primary"
                              icon={Sparkles}
                              onClick={() => handleStartEvaluation(sub.id)}
                              isLoading={evaluatingSubId === sub.id}
                            >
                              Evaluate
                            </Button>
                          ) : (
                            <Link to={`/teacher/evaluations/${sub.id}`}>
                              <Button size="sm" variant="secondary">
                                Review & Publish
                              </Button>
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Upload Submission Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title="Upload Student Submission"
        footer={
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Button variant="secondary" onClick={() => setIsUploadOpen(false)} disabled={isUploading}>
              Cancel
            </Button>
            <Button variant="primary" icon={UploadCloud} onClick={handleUploadSubmit} isLoading={isUploading}>
              Upload & Extract Text
            </Button>
          </div>
        }
      >
        <form onSubmit={handleUploadSubmit}>
          <div className="form-group">
            <label className="form-label">Target Assignment *</label>
            <select
              className="form-select"
              value={uploadAssignId}
              onChange={(e) => setUploadAssignId(e.target.value)}
              required
            >
              <option value="">Select Assignment...</option>
              {assignments.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.title} ({a.code || 'No Code'})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Assign to Student (Optional)</label>
            <select
              className="form-select"
              value={uploadStudentId}
              onChange={(e) => setUploadStudentId(e.target.value)}
            >
              <option value="">Choose Student (or upload on behalf of student)...</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.full_name} ({s.email})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Submission Document (PDF, DOCX, TXT) *</label>
            <input
              type="file"
              className="form-input"
              accept=".pdf,.docx,.txt,.md,.py,.java,.cpp,.c,.js"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              required
            />
          </div>
        </form>
      </Modal>
    </div>
  );
};
