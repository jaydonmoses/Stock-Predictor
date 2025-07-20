// Pass the companies data from Flask to JavaScript
        // Using JSON.parse to ensure robust parsing of the JSON string
        const companiesString = '{{ companies | tojson | safe }}';
        const companies = JSON.parse(companiesString);

        const input = document.getElementById('ticker');
        const suggestions = document.getElementById('suggestions');

        input.addEventListener('input', () => {
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
                // Use the static path for logos in JS, with onerror for fallback
                const logoSrc = `/static/logos/${company.ticker}.png`;
                div.innerHTML = `<img src="${logoSrc}" alt="${company.name} Logo" onerror="this.onerror=null;this.src='/static/logos/default.png';" loading="lazy"> ${company.name} (${company.ticker})`;

                div.addEventListener('click', () => {
                    input.value = company.ticker; // Set input to ticker when suggestion is clicked
                    suggestions.innerHTML = ''; // Hide suggestions
                });
                suggestions.appendChild(div);
            });
        });

        // Hide suggestions when clicking outside the autocomplete wrapper
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-wrapper')) {
                suggestions.innerHTML = '';
            }
        });