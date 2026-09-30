export const getStatusBadge = (status) => {
  switch (status?.toLowerCase()) {
    case 'published':
      return { label: 'Published', className: 'badge-success' };
    case 'approved':
      return { label: 'Approved', className: 'badge-success' };
    case 'under_review':
      return { label: 'Under Review', className: 'badge-warning' };
    case 'evaluated':
      return { label: 'Evaluated', className: 'badge-purple' };
    case 'evaluating':
    case 'processing':
      return { label: 'Evaluating...', className: 'badge-info' };
    case 'extracted':
      return { label: 'Ready for Eval', className: 'badge-info' };
    case 'pending':
      return { label: 'Pending', className: 'badge-warning' };
    case 'failed':
      return { label: 'Failed', className: 'badge-danger' };
    case 'active':
      return { label: 'Active', className: 'badge-success' };
    case 'closed':
      return { label: 'Closed', className: 'badge-danger' };
    default:
      return { label: status || 'Unknown', className: 'badge-info' };
  }
};

export const getOriginalityBadge = (riskLevel) => {
  switch (riskLevel?.toLowerCase()) {
    case 'low':
      return { label: 'Low Similarity', className: 'badge-success' };
    case 'medium':
    case 'moderate':
      return { label: 'Moderate Similarity', className: 'badge-warning' };
    case 'high':
      return { label: 'High Similarity', className: 'badge-danger' };
    default:
      return { label: 'Checked', className: 'badge-info' };
  }
};

export const getGradeColor = (grade) => {
  if (!grade) return 'var(--text-muted)';
  if (grade.startsWith('A')) return 'var(--success)';
  if (grade.startsWith('B')) return '#38bdf8';
  if (grade.startsWith('C')) return 'var(--warning)';
  if (grade.startsWith('D')) return '#f97316';
  return 'var(--danger)';
};
