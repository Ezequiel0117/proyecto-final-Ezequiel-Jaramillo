function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function showHistory(residueType) {
    const url = new URL(window.location);
    url.searchParams.set('residue', residueType);
    url.searchParams.delete('show_all');
    url.searchParams.delete('page'); 
    
    window.location.href = url.toString();
}

function showAllHistory() {
    const url = new URL(window.location);
    url.searchParams.set('show_all', 'true');
    url.searchParams.delete('residue');
    url.searchParams.delete('page'); 
    
    window.location.href = url.toString();
}

function goBack() {
    const url = new URL(window.location);
    url.search = '';
    window.location.href = url.toString();
}

document.addEventListener('DOMContentLoaded', function() {
    const residueType = getUrlParameter('residue');
    const showAll = getUrlParameter('show_all');
    
    if (showAll === 'true') {
        document.getElementById('residue-cards').style.display = 'none';
        document.getElementById('show-all-container').style.display = 'none';
        document.getElementById('history-section').style.display = 'block';
        document.getElementById('history-title').textContent = 'Historial Completo de Reciclaje';
    } else if (residueType) {
        document.getElementById('residue-cards').style.display = 'none';
        document.getElementById('show-all-container').style.display = 'none';
        document.getElementById('history-section').style.display = 'block';
        
        const titles = {
            'plastico': 'Historial de Plástico',
            'metal': 'Historial de Metal',
            'vidrio': 'Historial de Vidrio',
            'papel': 'Historial de Papel'
        };
        document.getElementById('history-title').textContent = titles[residueType] || 'Historial de Reciclaje';
    } else {
        document.getElementById('residue-cards').style.display = 'grid';
        document.getElementById('show-all-container').style.display = 'flex';
        document.getElementById('history-section').style.display = 'none';
    }
});