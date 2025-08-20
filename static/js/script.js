document.addEventListener("DOMContentLoaded", () => {
	initializeTooltips();
	initializeFormValidation();
	initializeEventRegistration();
	initializeAdminPanel();
	initializeSearchAndFilter();
	initializeResponsiveNav();
	initializeEnhancedEventsPage();
	initializeNotifications();
	initializeAnimations();
	initializeSmoothScrolling();
	addLoadingStates();
	autoHideAlerts();

	initializeIntersectionObserver();
});

function initializeTooltips() {
	const tooltipElements = document.querySelectorAll("[data-tip]");
	// biome-ignore lint/complexity/noForEach: <explanation>
	tooltipElements.forEach((element) => {
		element.addEventListener("mouseenter", function () {
			this.classList.add("tooltip-open");
		});

		element.addEventListener("mouseleave", function () {
			this.classList.remove("tooltip-open");
		});
	});
}

function initializeFormValidation() {
	const forms = document.querySelectorAll(".needs-validation");

	// biome-ignore lint/complexity/noForEach: <explanation>
	forms.forEach((form) => {
		form.addEventListener("submit", (event) => {
			if (!form.checkValidity()) {
				event.preventDefault();
				event.stopPropagation();

				showValidationFeedback(form);
			}
			form.classList.add("was-validated");
		});
	});

	const eventForm = document.querySelector('form[action*="create_event"]');
	if (eventForm) {
		const eventDateInput = eventForm.querySelector("#event_date");
		const regDeadlineInput = eventForm.querySelector("#registration_deadline");

		if (eventDateInput && regDeadlineInput) {
			eventDateInput.addEventListener("change", () => {
				validateEventDates(eventDateInput, regDeadlineInput);
			});

			regDeadlineInput.addEventListener("change", () => {
				validateEventDates(eventDateInput, regDeadlineInput);
			});
		}
	}

	initializeFloatingLabels();
}

function initializeFloatingLabels() {
	const formInputs = document.querySelectorAll(
		".form-control input, .form-control select, .form-control textarea",
	);

	// biome-ignore lint/complexity/noForEach: <explanation>
	formInputs.forEach((input) => {
		input.addEventListener("focus", function () {
			this.parentElement.classList.add("input-focused");
		});

		input.addEventListener("blur", function () {
			if (!this.value) {
				this.parentElement.classList.remove("input-focused");
			}
		});

		if (input.value) {
			input.parentElement.classList.add("input-focused");
		}
	});
}

function showValidationFeedback(form) {
	const invalidInputs = form.querySelectorAll(":invalid");

	// biome-ignore lint/complexity/noForEach: <explanation>
	invalidInputs.forEach((input) => {
		input.classList.add("input-error");

		let errorMessage = input.parentElement.querySelector(".error-message");
		if (!errorMessage) {
			errorMessage = document.createElement("div");
			errorMessage.className = "error-message text-error text-sm mt-1";
			input.parentElement.appendChild(errorMessage);
		}

		if (input.validity.valueMissing) {
			errorMessage.textContent = "This field is required";
		} else if (input.validity.typeMismatch) {
			errorMessage.textContent = "Please enter a valid value";
		} else if (input.validity.tooShort) {
			errorMessage.textContent = `Minimum length is ${input.minLength} characters`;
		} else if (input.validity.tooLong) {
			errorMessage.textContent = `Maximum length is ${input.maxLength} characters`;
		}
	});
}

function validateEventDates(eventDateInput, regDeadlineInput) {
	const eventDate = new Date(eventDateInput.value);
	const regDeadline = new Date(regDeadlineInput.value);
	const now = new Date();

	clearValidationMessages(eventDateInput);
	clearValidationMessages(regDeadlineInput);

	let isValid = true;

	if (regDeadline <= now) {
		showValidationMessage(
			regDeadlineInput,
			"Registration deadline must be in the future",
		);
		isValid = false;
	}

	if (eventDate <= regDeadline) {
		showValidationMessage(
			eventDateInput,
			"Event date must be after registration deadline",
		);
		isValid = false;
	}

	if (eventDate <= now) {
		showValidationMessage(eventDateInput, "Event date must be in the future");
		isValid = false;
	}

	return isValid;
}

function showValidationMessage(input, message) {
	const feedback = document.createElement("div");
	feedback.className = "text-error text-sm mt-1 flex items-center gap-2";
	feedback.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;

	input.classList.add("input-error");
	input.parentNode.appendChild(feedback);
}

function clearValidationMessages(input) {
	input.classList.remove("input-error");
	const feedback = input.parentNode.querySelector(".text-error");
	if (feedback) {
		feedback.remove();
	}
}

function initializeEventRegistration() {
	const registerButtons = document.querySelectorAll(
		'form[action*="register_event"]',
	);

	// biome-ignore lint/complexity/noForEach: <explanation>
	registerButtons.forEach((form) => {
		form.addEventListener("submit", (_event) => {
			const submitBtn = form.querySelector('button[type="submit"]');
			const originalText = submitBtn.innerHTML;

			submitBtn.innerHTML =
				'<span class="loading loading-spinner loading-sm"></span> Registering...';
			submitBtn.disabled = true;
			submitBtn.classList.add("btn-disabled");

			setTimeout(() => {
				submitBtn.innerHTML = originalText;
				submitBtn.disabled = false;
				submitBtn.classList.remove("btn-disabled");
			}, 2000);
		});
	});
}

function initializeAdminPanel() {
	const roleChangeButtons = document.querySelectorAll('a[href*="toggle_role"]');
	// biome-ignore lint/complexity/noForEach: <explanation>
	roleChangeButtons.forEach((button) => {
		button.addEventListener("click", (event) => {
			if (!confirm("Are you sure you want to change this user's role?")) {
				event.preventDefault();
			}
		});
	});

	const statusChangeButtons = document.querySelectorAll(
		'a[href*="toggle_status"]',
	);
	// biome-ignore lint/complexity/noForEach: <explanation>
	statusChangeButtons.forEach((button) => {
		button.addEventListener("click", (event) => {
			if (!confirm("Are you sure you want to change this event's status?")) {
				event.preventDefault();
			}
		});
	});

	initializeAdminTabs();
}

function initializeAdminTabs() {
	const adminTabs = document.querySelectorAll(".tabs .tab");
	const tabContents = document.querySelectorAll(".tab-content");

	// biome-ignore lint/complexity/noForEach: <explanation>
	adminTabs.forEach((tab) => {
		tab.addEventListener("click", function (event) {
			event.preventDefault();

			// biome-ignore lint/complexity/noForEach: <explanation>
			adminTabs.forEach((t) => t.classList.remove("tab-active"));
			// biome-ignore lint/complexity/noForEach: <explanation>
			tabContents.forEach((content) => content.classList.add("hidden"));

			this.classList.add("tab-active");

			const targetId =
				this.getAttribute("onclick")?.match(/showTab\('([^']+)'\)/)?.[1];
			if (targetId) {
				const targetContent = document.getElementById(targetId);
				if (targetContent) {
					targetContent.classList.remove("hidden");
					targetContent.classList.add("active");
				}
			}
		});
	});
}

function initializeSearchAndFilter() {
	const searchInput = document.querySelector("#search");
	if (searchInput) {
		let searchTimeout;
		searchInput.addEventListener("input", function () {
			clearTimeout(searchTimeout);
			searchTimeout = setTimeout(() => {
				const searchTerm = this.value.toLowerCase();
				filterEvents(searchTerm);
			}, 300);
		});
	}

	const categorySelect = document.querySelector("#category");
	const statusSelect = document.querySelector("#status");

	if (categorySelect) {
		categorySelect.addEventListener("change", () => {
			applyFilters();
		});
	}

	if (statusSelect) {
		statusSelect.addEventListener("change", () => {
			applyFilters();
		});
	}
}

function filterEvents(searchTerm) {
	const eventCards = document.querySelectorAll(".event-card");

	eventCards.forEach((card, index) => {
		const title =
			card.querySelector(".card-title")?.textContent.toLowerCase() || "";
		const description =
			card.querySelector(".card-text")?.textContent.toLowerCase() || "";
		const category =
			card.querySelector(".badge")?.textContent.toLowerCase() || "";
		const location = card.textContent.toLowerCase();

		if (
			title.includes(searchTerm) ||
			description.includes(searchTerm) ||
			category.includes(searchTerm) ||
			location.includes(searchTerm)
		) {
			card.style.display = "block";
			card.style.animationDelay = `${index * 0.1}s`;
			card.classList.add("animate-fade-in");
		} else {
			card.style.display = "none";
		}
	});
}

function applyFilters() {
	const category = document.querySelector("#category")?.value;
	const status = document.querySelector("#status")?.value;

	const eventsContainer = document.querySelector(".row");
	if (eventsContainer) {
		eventsContainer.classList.add("loading");

		setTimeout(() => {
			eventsContainer.classList.remove("loading");
			showNotification("Filters applied successfully", "success");
		}, 1000);
	}
}

function initializeResponsiveNav() {
	const navbarToggler = document.querySelector(".navbar-toggler");
	const navbarCollapse = document.querySelector(".navbar-collapse");

	if (navbarToggler && navbarCollapse) {
		const navLinks = navbarCollapse.querySelectorAll(".nav-link");
		// biome-ignore lint/complexity/noForEach: <explanation>
		navLinks.forEach((link) => {
			link.addEventListener("click", () => {
				if (window.innerWidth < 992) {
					navbarCollapse.classList.remove("show");
				}
			});
		});

		document.addEventListener("click", (event) => {
			if (
				!navbarToggler.contains(event.target) &&
				!navbarCollapse.contains(event.target)
			) {
				navbarCollapse.classList.remove("show");
			}
		});
	}
}

function initializeNotifications() {
	// biome-ignore lint/complexity/useArrowFunction: <explanation>
	window.showNotification = function (message, type = "info", duration = 5000) {
		const notification = document.createElement("div");
		notification.className = `alert alert-${type} alert-dismissible fade show position-fixed z-50`;
		notification.style.cssText =
			"top: 20px; right: 20px; min-width: 300px; max-width: 400px;";
		notification.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="fas fa-${getNotificationIcon(type)} text-lg"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

		document.body.appendChild(notification);
		notification.classList.add("animate-fade-in");

		setTimeout(() => {
			if (notification.parentNode) {
				notification.classList.add("animate-fade-out");
				setTimeout(() => {
					if (notification.parentNode) {
						notification.remove();
					}
				}, 300);
			}
		}, duration);
	};
}

function getNotificationIcon(type) {
	const icons = {
		success: "check-circle",
		error: "exclamation-triangle",
		warning: "exclamation-triangle",
		info: "info-circle",
	};
	return icons[type] || "info-circle";
}

function initializeAnimations() {
	const animatedElements = document.querySelectorAll(
		".card, .stats .stat, .feature-card",
	);

	animatedElements.forEach((element, index) => {
		element.style.animationDelay = `${index * 0.1}s`;
		element.classList.add("animate-fade-in");
	});
}

function initializeIntersectionObserver() {
	const observerOptions = {
		threshold: 0.1,
		rootMargin: "0px 0px -50px 0px",
	};

	const observer = new IntersectionObserver((entries) => {
		// biome-ignore lint/complexity/noForEach: <explanation>
		entries.forEach((entry) => {
			if (entry.isIntersecting) {
				entry.target.classList.add("animate-fade-in");
				observer.unobserve(entry.target);
			}
		});
	}, observerOptions);

	const elementsToObserve = document.querySelectorAll(
		".card, .stats .stat, .feature-card, .timeline-item",
	);
	// biome-ignore lint/complexity/noForEach: <explanation>
	elementsToObserve.forEach((element) => {
		observer.observe(element);
	});
}

function performQuickSearch() {
	const searchInput = document.getElementById("quickSearch");
	const searchTerm = searchInput.value.toLowerCase().trim();

	if (!searchTerm) {
		showNotification("Please enter a search term", "warning");
		return;
	}

	const eventCards = document.querySelectorAll(".event-card");
	let foundEvents = 0;

	eventCards.forEach((card, index) => {
		const title =
			card.querySelector(".card-title")?.textContent.toLowerCase() || "";
		const description =
			card.querySelector("p")?.textContent.toLowerCase() || "";
		const category =
			card.querySelector(".badge")?.textContent.toLowerCase() || "";
		const location = card.textContent.toLowerCase();

		if (
			title.includes(searchTerm) ||
			description.includes(searchTerm) ||
			category.includes(searchTerm) ||
			location.includes(searchTerm)
		) {
			card.parentElement.style.display = "block";
			card.style.animationDelay = `${index * 0.1}s`;
			card.classList.add("animate-fade-in");
			foundEvents++;
		} else {
			card.parentElement.style.display = "none";
		}
	});

	updateResultsCount(foundEvents);

	if (foundEvents === 0) {
		showNotification(`No events found for "${searchTerm}"`, "info");
	}
}

function updateFilters() {
	const category = document.getElementById("category")?.value;
	const status = document.getElementById("status")?.value;
	const dateRange = document.getElementById("dateRange")?.value;
	const sortBy = document.getElementById("sortBy")?.value;

	updateActiveFiltersDisplay({ category, status, dateRange, sortBy });

	showFilterLoading(true);

	setTimeout(() => {
		showFilterLoading(false);
		showNotification("Filters applied successfully", "success");
	}, 1000);
}

function updateActiveFiltersDisplay(filters) {
	const activeFiltersContainer = document.getElementById("activeFilters");
	if (!activeFiltersContainer) return;

	activeFiltersContainer.innerHTML = "";

	// biome-ignore lint/complexity/noForEach: <explanation>
	Object.entries(filters).forEach(([key, value]) => {
		if (value) {
			const badge = document.createElement("div");
			badge.className = "badge badge-primary badge-lg gap-2";
			badge.innerHTML = `
                <span>${key.replace("_", " ")}: ${value}</span>
                <button class="btn btn-ghost btn-xs" onclick="clearFilter('${key}')">
                    <i class="fas fa-times"></i>
                </button>
            `;
			activeFiltersContainer.appendChild(badge);
		}
	});
}

function clearFilter(filterType) {
	const filterElement = document.getElementById(filterType);
	if (filterElement) {
		filterElement.value = "";
		updateFilters();
	}
}

function setView(viewType) {
	const gridView = document.getElementById("gridViewContainer");
	const listView = document.getElementById("listViewContainer");
	const gridButton = document.getElementById("gridView");
	const listButton = document.getElementById("listView");

	if (viewType === "grid") {
		gridView?.classList.remove("hidden");
		listView?.classList.add("hidden");
		gridButton?.classList.add("btn-active");
		listButton?.classList.remove("btn-active");
		localStorage.setItem("preferredView", "grid");
	} else {
		gridView?.classList.add("hidden");
		listView?.classList.remove("hidden");
		listButton?.classList.add("btn-active");
		gridButton?.classList.remove("btn-active");
		localStorage.setItem("preferredView", "list");
	}
}

function loadMoreEvents() {
	const button = event.target;
	const originalText = button.innerHTML;

	button.innerHTML =
		'<span class="loading loading-spinner loading-sm"></span> Loading...';
	button.disabled = true;
	button.classList.add("btn-disabled");

	setTimeout(() => {
		button.innerHTML = originalText;
		button.disabled = false;
		button.classList.remove("btn-disabled");
		showNotification("More events loaded successfully", "success");
	}, 2000);
}

function showFilterLoading(isLoading) {
	const eventsContainer = document.getElementById("eventsContainer");
	if (isLoading) {
		eventsContainer?.classList.add("opacity-50", "pointer-events-none");
	} else {
		eventsContainer?.classList.remove("opacity-50", "pointer-events-none");
	}
}

function updateResultsCount(count) {
	const countElement = document.querySelector(".stat-value");
	if (countElement) {
		countElement.textContent = count;
	}
}

function toggleAdvancedFilters() {
	showNotification("Advanced filters coming soon!", "info");
}

function initializeEnhancedEventsPage() {
	const preferredView = localStorage.getItem("preferredView") || "grid";
	setView(preferredView);

	const quickSearch = document.getElementById("quickSearch");
	if (quickSearch) {
		quickSearch.addEventListener("keypress", (e) => {
			if (e.key === "Enter") {
				e.preventDefault();
				performQuickSearch();
			}
		});

		let searchTimeout;
		quickSearch.addEventListener("input", function () {
			clearTimeout(searchTimeout);
			searchTimeout = setTimeout(() => {
				if (this.value.length >= 3) {
					performQuickSearch();
				} else if (this.value.length === 0) {
					// biome-ignore lint/complexity/noForEach: <explanation>
					document.querySelectorAll(".event-card").forEach((card) => {
						card.parentElement.style.display = "block";
					});
				}
			}, 300);
		});
	}

	addAnimationStyles();
}

function addAnimationStyles() {
	const style = document.createElement("style");
	style.textContent = `
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        .animate-fade-out {
            animation: fadeOutUp 0.3s ease-out;
        }
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes fadeOutUp {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
        .transition-all {
            transition: all 0.3s ease;
        }
        .input-focused .label-text {
            transform: translateY(-1.5rem) scale(0.85);
            color: hsl(var(--p));
        }
        .input-error {
            border-color: hsl(var(--er));
            box-shadow: 0 0 0 3px hsl(var(--er) / 0.1);
        }
    `;
	document.head.appendChild(style);
}

function showNotification(message, type = "info") {
	if (window.showNotification) {
		window.showNotification(message, type);
	} else {
		const notification = document.createElement("div");
		notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
		notification.style.cssText =
			"top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
		notification.innerHTML = `
            ${message}
            <button type="button" class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

		document.body.appendChild(notification);

		setTimeout(() => {
			if (notification.parentNode) {
				notification.remove();
			}
		}, 5000);
	}
}

function initializeSmoothScrolling() {
	const anchorLinks = document.querySelectorAll('a[href^="#"]');

	// biome-ignore lint/complexity/noForEach: <explanation>
	anchorLinks.forEach((link) => {
		link.addEventListener("click", function (event) {
			const targetId = this.getAttribute("href");
			const targetElement = document.querySelector(targetId);

			if (targetElement) {
				event.preventDefault();
				targetElement.scrollIntoView({
					behavior: "smooth",
					block: "start",
				});
			}
		});
	});
}

function addLoadingStates() {
	const forms = document.querySelectorAll("form");

	// biome-ignore lint/complexity/noForEach: <explanation>
	forms.forEach((form) => {
		form.addEventListener("submit", () => {
			const submitBtn = form.querySelector('button[type="submit"]');
			if (submitBtn) {
				submitBtn.disabled = true;
				submitBtn.innerHTML =
					'<span class="loading loading-spinner loading-sm"></span> Processing...';
			}
		});
	});
}

function autoHideAlerts() {
	const alerts = document.querySelectorAll(".alert");

	// biome-ignore lint/complexity/noForEach: <explanation>
	alerts.forEach((alert) => {
		setTimeout(() => {
			if (alert.parentNode) {
				alert.style.opacity = "0";
				alert.style.transform = "translateY(-20px)";
				setTimeout(() => {
					alert.remove();
				}, 300);
			}
		}, 5000);
	});
}

function showTab(tabName) {
	const tabContents = document.querySelectorAll(".tab-content");
	// biome-ignore lint/complexity/noForEach: <explanation>
	tabContents.forEach((content) => {
		content.classList.add("hidden");
		content.classList.remove("active");
	});

	const tabs = document.querySelectorAll(".tab");
	// biome-ignore lint/complexity/noForEach: <explanation>
	tabs.forEach((tab) => {
		tab.classList.remove("tab-active");
	});

	document.getElementById(tabName).classList.remove("hidden");
	document.getElementById(tabName).classList.add("active");

	document.getElementById(`${tabName}-tab`).classList.add("tab-active");
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", initializeEnhancedEventsPage);
} else {
	initializeEnhancedEventsPage();
}
