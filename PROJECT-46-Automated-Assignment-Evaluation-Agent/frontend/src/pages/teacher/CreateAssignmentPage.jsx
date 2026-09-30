import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Sliders,
  UploadCloud,
  CheckCircle2,
  Plus,
  Trash2,
  BookOpen,
  ArrowRight,
  ArrowLeft,
  FileCheck,
} from 'lucide-react';
import { assignmentService } from '../../services/assignmentService';
import { rubricService } from '../../services/rubricService';
import { studentService } from '../../services/studentService';
import { useToast } from '../../hooks/useToast';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, Textarea } from '../../components/common/Input';

export const CreateAssignmentPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Form State
  const [title, setTitle] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [instructions, setInstructions] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [maxScore, setMaxScore] = useState(100);

  // Rubric State
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [criteria, setCriteria] = useState([
    { name: 'Understanding & Concept', description: 'Theoretical grasp of key principles', max_points: 20, evaluation_guidelines: '' },
    { name: 'Implementation & Methodology', description: 'Execution and functional correctness', max_points: 35, evaluation_guidelines: '' },
    { name: 'Code Quality & Structure', description: 'Clean architecture and standards', max_points: 25, evaluation_guidelines: '' },
    { name: 'Testing & Documentation', description: 'Verification, tests, and explanations', max_points: 20, evaluation_guidelines: '' },
  ]);

  // Reference Files
  const [referenceFile, setReferenceFile] = useState(null);
  const [refTitle, setRefTitle] = useState('');

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const t = await rubricService.getTemplates();
        setTemplates(t);
      } catch (err) {
        console.error('Failed to load templates', err);
      }
    };
    loadTemplates();
  }, []);

  const handleApplyTemplate = (tplId) => {
    setSelectedTemplate(tplId);
    const found = templates.find((t) => t.id === tplId);
    if (found) {
      setCriteria(
        found.criteria.map((c) => ({
          name: c.name,
          description: c.description,
          max_points: c.max_points,
          evaluation_guidelines: c.guidelines || '',
        }))
      );
      toast.info(`Applied '${found.title}' rubric template.`);
    }
  };

  const handleAddCriterion = () => {
    setCriteria((prev) => [
      ...prev,
      { name: 'New Criterion', description: '', max_points: 15, evaluation_guidelines: '' },
    ]);
  };

  const handleRemoveCriterion = (index) => {
    if (criteria.length <= 1) {
      toast.warning('A rubric requires at least one criterion.');
      return;
    }
    setCriteria((prev) => prev.filter((_, i) => i !== index));
  };

  const handleCriterionChange = (index, field, value) => {
    setCriteria((prev) =>
      prev.map((c, i) => {
        if (i === index) {
          return { ...c, [field]: field === 'max_points' ? parseFloat(value) || 0 : value };
        }
        return c;
      })
    );
  };

  const totalPoints = criteria.reduce((sum, c) => sum + (parseFloat(c.max_points) || 0), 0);

  const handleSubmit = async () => {
    if (!title || !instructions) {
      toast.error('Title and Instructions are required.');
      setStep(1);
      return;
    }

    setIsLoading(true);
    try {
      const payload = {
        title,
        code: code || null,
        description,
        instructions,
        max_score: totalPoints || maxScore,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        status: 'active',
        rubric_title: `Rubric for ${title}`,
        rubric_criteria: criteria.map((c, idx) => ({
          name: c.name,
          description: c.description,
          max_points: c.max_points,
          weight: 1.0,
          order_index: idx,
          evaluation_guidelines: c.evaluation_guidelines || c.description,
        })),
      };

      const created = await assignmentService.createAssignment(payload);

      // Upload reference document if provided
      if (referenceFile) {
        try {
          await assignmentService.uploadReference(created.id, refTitle || referenceFile.name, referenceFile);
          toast.success('Reference material indexed in ChromaDB for RAG context.');
        } catch (uploadErr) {
          toast.warning('Assignment created, but reference document upload encountered an issue.');
        }
      }

      toast.success('Assignment and rubric created successfully!');
      navigate(`/teacher/assignments/${created.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create assignment.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Create New Assignment</h1>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          Configure assignment guidelines, set up rubric criteria, and upload knowledge base reference materials.
        </p>
      </div>

      {/* Stepper Navigation */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 1.5rem',
          borderRadius: 'var(--radius-lg)',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xs)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: step >= 1 ? 'var(--text-primary)' : 'var(--text-muted)' }}>
          <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: step >= 1 ? 'var(--primary-gradient)' : '#f1f5f9', color: step >= 1 ? 'white' : 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 700 }}>
            1
          </span>
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Assignment Details</span>
        </div>
        <ArrowRight size={16} color="var(--text-muted)" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: step >= 2 ? 'var(--text-primary)' : 'var(--text-muted)' }}>
          <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: step >= 2 ? 'var(--primary-gradient)' : '#f1f5f9', color: step >= 2 ? 'white' : 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 700 }}>
            2
          </span>
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Rubric Builder</span>
        </div>
        <ArrowRight size={16} color="var(--text-muted)" />
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: step >= 3 ? 'var(--text-primary)' : 'var(--text-muted)' }}>
          <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: step >= 3 ? 'var(--primary-gradient)' : '#f1f5f9', color: step >= 3 ? 'white' : 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem', fontWeight: 700 }}>
            3
          </span>
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Reference Documents</span>
        </div>
      </div>

      {/* Step 1: Basic Information */}
      {step === 1 && (
        <Card title="Step 1: Assignment Brief & Guidelines">
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }}>
            <Input
              label="Assignment Title *"
              placeholder="e.g. Distributed Systems Raft Consensus Protocol"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <Input
              label="Course Code / ID"
              placeholder="e.g. CS-602-A2"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </div>

          <Input
            label="Short Description"
            placeholder="Brief overview of the assignment topic..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <Textarea
            label="Detailed Instructions / Problem Statement *"
            placeholder="Enter the complete assignment instructions, required modules, edge cases, and expected deliverables..."
            rows={7}
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            required
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Due Date & Time"
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
            <Input
              label="Target Max Score"
              type="number"
              value={totalPoints || maxScore}
              disabled
              helperText="Auto-computed from rubric criteria total"
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
            <Button
              variant="primary"
              icon={ArrowRight}
              onClick={() => {
                if (!title || !instructions) {
                  toast.error('Please provide an assignment title and instructions.');
                  return;
                }
                setStep(2);
              }}
            >
              Continue to Rubric
            </Button>
          </div>
        </Card>
      )}

      {/* Step 2: Rubric Builder */}
      {step === 2 && (
        <Card
          title="Step 2: Rubric Criteria & Standards"
          subtitle="Define the multi-criteria standards evaluated by the AI"
          action={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Total Points:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--primary-500)' }}>
                {totalPoints} pts
              </span>
            </div>
          }
        >
          {/* Preset Templates */}
          {templates.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Apply Pre-configured Template:</label>
              <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
                {templates.map((tpl) => (
                  <button
                    key={tpl.id}
                    type="button"
                    onClick={() => handleApplyTemplate(tpl.id)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: selectedTemplate === tpl.id ? 'var(--primary-500)' : '#f8fafc',
                      border: '1px solid',
                      borderColor: selectedTemplate === tpl.id ? 'var(--primary-500)' : 'var(--border-subtle)',
                      color: selectedTemplate === tpl.id ? 'white' : 'var(--text-primary)',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                    }}
                  >
                    <Sparkles size={13} />
                    {tpl.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Criteria List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {criteria.map((c, idx) => (
              <div
                key={idx}
                style={{
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: '#f8fafc',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 100px 40px', gap: '0.75rem', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Criterion Name (e.g. Code Quality)"
                    value={c.name}
                    onChange={(e) => handleCriterionChange(idx, 'name', e.target.value)}
                    style={{ padding: '0.5rem 0.75rem' }}
                  />
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <input
                      type="number"
                      min="1"
                      className="form-input"
                      value={c.max_points}
                      onChange={(e) => handleCriterionChange(idx, 'max_points', e.target.value)}
                      style={{ padding: '0.5rem 0.5rem', textAlign: 'center' }}
                    />
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>pts</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveCriterion(idx)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                <input
                  type="text"
                  className="form-input"
                  placeholder="Evaluation guidelines for the AI evaluator (e.g. Look for clean modular functions and unit tests)..."
                  value={c.description}
                  onChange={(e) => handleCriterionChange(idx, 'description', e.target.value)}
                  style={{ fontSize: '0.825rem', padding: '0.5rem 0.75rem' }}
                />
              </div>
            ))}

            <Button variant="secondary" size="sm" icon={Plus} onClick={handleAddCriterion} style={{ alignSelf: 'flex-start' }}>
              Add Criterion
            </Button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.75rem' }}>
            <Button variant="secondary" icon={ArrowLeft} onClick={() => setStep(1)}>
              Back
            </Button>
            <Button variant="primary" icon={ArrowRight} onClick={() => setStep(3)}>
              Continue to References
            </Button>
          </div>
        </Card>
      )}

      {/* Step 3: Reference Materials & Confirmation */}
      {step === 3 && (
        <Card title="Step 3: Reference Materials & Verification" subtitle="Upload solution manuals or reference texts for RAG grounding">
          <div
            style={{
              border: '2px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              marginBottom: '1.5rem',
            }}
          >
            <UploadCloud size={40} color="var(--primary-500)" style={{ margin: '0 auto 0.75rem' }} />
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Upload Knowledge Document (Optional)</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem', marginBottom: '1rem' }}>
              Supports PDF, DOCX, TXT. Contents will be vectorized into ChromaDB for semantic retrieval.
            </p>
            <input
              type="file"
              id="ref-upload"
              style={{ display: 'none' }}
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setReferenceFile(e.target.files[0]);
                  setRefTitle(e.target.files[0].name);
                  toast.success(`Selected file: ${e.target.files[0].name}`);
                }
              }}
            />
            <label htmlFor="ref-upload">
              <span className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                Browse File
              </span>
            </label>

            {referenceFile && (
              <div style={{ marginTop: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '6px 12px', borderRadius: 'var(--radius-full)', background: 'var(--purple-bg)', color: 'var(--purple-text)', border: '1px solid var(--purple-border)', fontSize: '0.85rem' }}>
                <FileCheck size={16} />
                <span>{referenceFile.name} ({(referenceFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>

          {/* Summary Box */}
          <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-md)', backgroundColor: '#f8fafc', border: '1px solid var(--border-subtle)', marginBottom: '1.5rem' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.6rem', color: 'var(--text-primary)' }}>Ready to Publish:</h4>
            <ul style={{ listStyle: 'none', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <li>• <strong>Title:</strong> {title}</li>
              <li>• <strong>Rubric:</strong> {criteria.length} criteria totaling {totalPoints} points</li>
              <li>• <strong>RAG Vectorizing:</strong> {referenceFile ? `Yes (${referenceFile.name})` : 'Instructions only'}</li>
            </ul>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button variant="secondary" icon={ArrowLeft} onClick={() => setStep(2)}>
              Back
            </Button>
            <Button
              variant="success"
              icon={CheckCircle2}
              onClick={handleSubmit}
              isLoading={isLoading}
            >
              Create & Activate Assignment
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
