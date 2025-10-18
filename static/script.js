
function openEditModal(id, title, desc){
  const modal = document.getElementById('editModal');
  modal.setAttribute('aria-hidden', 'false');
  document.getElementById('editTitle').value = title;
  document.getElementById('editDesc').value = desc || '';
  document.getElementById('editForm').action = '/edit/' + id;
}
function closeEditModal(){
  const modal = document.getElementById('editModal');
  modal.setAttribute('aria-hidden', 'true');
}
document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeEditModal(); });
