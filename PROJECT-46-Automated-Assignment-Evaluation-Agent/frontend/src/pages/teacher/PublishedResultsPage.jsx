import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Award, Download, Filter, FileText, CheckCircle2, UserCheck, Eye } from 'lucide-react';
import { resultService } from '../../services/resultService';
import { assignmentService } from '../../services/assignmentService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { formatDate, formatPercentage } from '../../utils/formatters';
import { getGradeColor } from '../../utils/statusBadges';

export const PublishedResultsPage = () => {
  const [results, setResults] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const toast = useToast();

  const loadData = async () => {
    try {
      const [resData, assignData] = await Promise.all([
        resultService.listResults({ assignmentId: selectedAssignment || null }),
        assignmentService.listAssignments(),
      ]);
      setResults(resData);
      setAssignments(assignData);
    } catch (err) {
      toast.error('Failed to load published grades.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedAssignment]);

  const handleExportCSV = () => {
    if (results.length === 0) {
      toast.warning('No results to export.');
      return;
    }

    const headers = ['Student Name', 'Student Email', 'Assignment', 'Score', 'Max Score', 'Percentage', 'Letter Grade', 'Published At'];
    const rows = results.map((r) => [
      `"${r.student?.full_name || ''}"`,
      `"${r.student?.email || ''}"`,
      `"${r.assignment_title || ''}"`,
      r.final_score,
      r.max_score,
      r.percentage,
      `"${r.letter_grade || ''}"`,
      `"${formatDate(r.published_at)}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Published_Grades_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('CSV Grade report exported.');
  };

  if (isLoading) {
    return <Loader message="Loading published grade rosters..." size="lg" />;
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Published Grades & Reports</h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Official released assignment evaluations accessible to enrolled students.
          </p>
        </div>

        <Button variant="secondary" icon={Download} onClick={handleExportCSV}>
          Export CSV Roster
        </Button>
      </div>

      {/* Filter */}
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          alignItems: 'center',
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <Filter size={16} /> Filter Assignment:
        </div>

        <select
          className="form-select"
          value={selectedAssignment}
          onChange={(e) => setSelectedAssignment(e.target.value)}
          style={{ width: 'auto', minWidth: '240px' }}
        >
          <option value="">All Assignments</option>
          {assignments.map((a) => (
            <option key={a.id} value={a.id}>
              {a.title}
            </option>
          ))}
        </select>
      </div>

      {/* Published Grades Table */}
      <Card>
        {results.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <Award size={40} color="var(--primary-500)" style={{ margin: '0 auto 0.75rem' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>No published grades yet</h3>
            <p style={{ marginTop: '0.2rem' }}>
              Submissions that are reviewed and approved by instructors will appear here.
            </p>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Assignment</th>
                  <th>Final Score</th>
                  <th>Percentage</th>
                  <th>Grade</th>
                  <th>Published Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {results.map((res) => (
                  <tr key={res.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{res.student?.full_name || `Student #${res.student_id}`}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{res.student?.email}</div>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{res.assignment_title}</td>
                    <td>
                      <strong style={{ color: 'var(--text-primary)' }}>
                        {res.final_score} / {res.max_score}
                      </strong>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--primary-500)' }}>
                      {formatPercentage(res.percentage)}
                    </td>
                    <td>
                      <span
                        style={{
                          fontSize: '1rem',
                          fontWeight: 800,
                          color: getGradeColor(res.letter_grade),
                        }}
                      >
                        {res.letter_grade || '—'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {formatDate(res.published_at)}
                    </td>
                    <td>
                      <Link to={`/teacher/evaluations/${res.submission_id}`}>
                        <Button size="sm" variant="secondary" icon={Eye}>
                          View Report
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
