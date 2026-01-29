document.addEventListener('DOMContentLoaded', () => {
            const navLinks = document.querySelectorAll('.nav-link');
            const sections = document.querySelectorAll('section');
            const hamburger = document.getElementById('hamburger-menu');
            const navMenu = document.getElementById('nav-menu');
            const revealElements = document.querySelectorAll('.reveal');
            const varietiesGrid = document.getElementById('apple-varieties-grid');

            // --- Hamburger Menu Toggle ---
            hamburger.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                hamburger.classList.toggle('active');
            });

            // --- Smooth Scroll for Navigation Links and internal buttons ---
            const scrollToElement = (targetSelector) => {
                const targetElement = document.querySelector(targetSelector);
                if (targetElement) {
                    // Close hamburger menu if open
                    if (navMenu.classList.contains('active')) {
                        navMenu.classList.remove('active');
                        hamburger.classList.remove('active');
                    }
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            };

            navLinks.forEach(link => {
                link.addEventListener('click', (event) => {
                    event.preventDefault(); // Prevent default browser action for javascript:void(0)
                    const targetId = link.dataset.sectionId;
                    if (targetId) {
                        scrollToElement(`#${targetId}`);
                    }
                });
            });

            // For the "Explore Our Varieties" button in the hero section
            document.querySelector('.hero-section .btn').addEventListener('click', (event) => {
                const targetSelector = event.target.dataset.target;
                if (targetSelector) {
                    scrollToElement(targetSelector);
                }
            });

            // --- Active Nav Link Highlight on Scroll ---
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        navLinks.forEach(link => {
                            link.classList.remove('active');
                            // Compare data-section-id with section's id
                            if (link.dataset.sectionId === entry.target.id) {
                                link.classList.add('active');
                            }
                        });
                    }
                });
            }, { rootMargin: '-50% 0px -49% 0px' }); // Activates link when section is roughly in the middle

            sections.forEach(section => {
                sectionObserver.observe(section);
            });

            // --- Reveal-on-Scroll Effect ---
            const revealObserverOptions = {
                root: null,
                rootMargin: '0px',
                threshold: 0.2 // Reveal when 20% of the element is visible
            };

            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('active');
                        observer.unobserve(entry.target); // Stop observing once revealed
                    }
                });
            }, revealObserverOptions);

            revealElements.forEach(element => {
                revealObserver.observe(element);
            });

            // --- API Data Fetch and Fallback for Apple Varieties ---
            const MOCK_APPLE_DATA = [
                { "id": 1, "name": "Gala Apple", "price": 2.49, "description": "Sweet and crisp with a mild flavor, perfect for snacking.", "imagePlaceholder": "ADD IMAGE" },
                { "id": 2, "name": "Fuji Apple", "price": 2.99, "description": "Known for its sweetness and juiciness, great in salads.", "imagePlaceholder": "ADD IMAGE" },
                { "id": 3, "name": "Honeycrisp Apple", "price": 3.99, "description": "Explosively crisp and sweet-tart, a premium choice.", "imagePlaceholder": "ADD IMAGE" },
                { "id": 4, "name": "Granny Smith Apple", "price": 1.99, "description": "Tart and firm, excellent for baking and cooking.", "imagePlaceholder": "ADD IMAGE" },
                { "id": 5, "name": "Red Delicious Apple", "price": 2.29, "description": "Mildly sweet and crunchy, a classic red apple.", "imagePlaceholder": "ADD IMAGE" },
                { "id": 6, "name": "Pink Lady Apple", "price": 3.29, "description": "Balanced sweet-tart flavor with a crisp texture.", "imagePlaceholder": "ADD IMAGE" }
            ];

            const renderAppleCards = (apples) => {
                if (!varietiesGrid) return;
                varietiesGrid.innerHTML = ''; // Clear existing placeholder cards
                apples.forEach(apple => {
                    const card = document.createElement('div');
                    card.classList.add('apple-card', 'glass-card');
                    card.innerHTML = `
                        <div class="image-placeholder">${apple.imagePlaceholder}</div>
                        <div class="apple-card-content">
                            <h3>${apple.name}</h3>
                            <p>${apple.description}</p>
                            <span class="apple-card-price">$${apple.price.toFixed(2)} / lb</span>
                            <button type="button" class="btn">Add to Cart</button>
                        </div>
                    `;
                    varietiesGrid.appendChild(card);
                });
            };

            const fetchAppleData = async () => {
                try {
                    // Simulate network delay and potential failure
                    const shouldFail = Math.random() < 0.2; // 20% chance of fetch failure
                    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate 1.5s network latency

                    if (shouldFail) {
                        throw new Error('Simulated network error or API failure.');
                    }

                    // For this project, we're using reliable mock data for the content structure
                    // to ensure consistent visual output without external API dependency on content.
                    // The 'fetch' demonstration is for the network interaction pattern.
                    // If a real external API was to be used for actual apple data, it would be here:
                    // const response = await fetch('https://some-real-fruit-api.com/apples');
                    // if (!response.ok) throw new Error('Network response was not ok');
                    // const apiData = await response.json();
                    // const processedApiData = apiData.slice(0, 6).map(item => ({
                    //     id: item.id,
                    //     name: item.name || 'API Apple',
                    //     price: item.price || (Math.random() * 2 + 1).toFixed(2),
                    //     description: item.description || 'A fresh and tasty apple from the API.',
                    //     imagePlaceholder: "ADD IMAGE"
                    // }));
                    // renderAppleCards(processedApiData);

                    // Successfully simulated fetch. Render the structured mock data.
                    renderAppleCards(MOCK_APPLE_DATA);

                } catch (error) {
                    console.error('Failed to fetch apple data (simulated):', error);
                    // On failure, do nothing. The initial static placeholder cards
                    // already in the HTML will remain visible, fulfilling the fallback rule.
                    // No error messages are shown to the user in the UI.
                }
            };

            // Attempt to fetch and render dynamic data, replacing initial placeholders on success.
            fetchAppleData();
        });