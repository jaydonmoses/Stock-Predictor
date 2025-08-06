document.addEventListener('DOMContentLoaded', () => {
    let companies = [];
    const input = document.getElementById('ticker');
    const suggestions = document.getElementById('suggestions');

    // Fetch companies data when the page loads
    fetch('/api/companies')
        .then(response => response.json())
        .then(data => {
            companies = data;
        })
        .catch(error => console.error('Error fetching companies:', error));

    // Debounce function to limit how often we search
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    const updateSuggestions = debounce(() => {
        const value = input.value.toLowerCase();
        suggestions.innerHTML = ''; // Clear previous suggestions

        if (!value) {
            return; // Don't show suggestions if input is empty
        }

            const matches = companies.filter(company =>
                company.name.toLowerCase().includes(value) ||
                company.ticker.toLowerCase().includes(value)
            ).slice(0, 10); // Limit to top 10 matches

            matches.forEach(company => {
                const div = document.createElement('div');
                div.classList.add('suggestion');
                
                // Create logo with API fallbacks
                const logoHtml = `
                    <div class="logo-wrapper w-6 h-6 mr-2 rounded-full bg-white flex items-center justify-center">
                        <img src="https://logo.clearbit.com/${company.ticker.toLowerCase()}.com" 
                             alt="${company.name} Logo" 
                             class="w-5 h-5 rounded-full object-contain"
                             onerror="this.onerror=null;this.src='https://api.logo.dev/${company.ticker.toUpperCase()}?token=pk_X1RlL8nWQ8ykU9TvaXQYBQ&format=png&size=200';if(this.onerror){this.onerror=null;this.parentElement.innerHTML='<div class=\\'w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold text-xs\\'>${company.ticker.substring(0,2)}</div>';}" 
                             loading="lazy">
                    </div>
                `;
                
                div.innerHTML = `${logoHtml} <span>${company.name} (${company.ticker})</span>`;

                div.addEventListener('click', () => {
                    input.value = company.ticker; // Set input to ticker when suggestion is clicked
                    suggestions.innerHTML = ''; // Hide suggestions
                });
                suggestions.appendChild(div);
            });
        }, 300); // 300ms debounce delay

        input.addEventListener('input', updateSuggestions);

        // Hide suggestions when clicking outside the autocomplete wrapper
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-wrapper')) {
                suggestions.innerHTML = '';
            }
        });
    });