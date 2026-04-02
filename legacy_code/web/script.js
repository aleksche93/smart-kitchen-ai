/* ============================================
   GLOBAL STATE
   ============================================ */
let globalIngredients = [];
let globalKnown = [];
window.currentIngredients = [];

// ChefPersona state
let chefState = {
    mode: "idle", // idle | categories | dishes | recipe
    lastDish: null
};

const categoryIcons = {
    "гарячі страви": "🔥",
    "холодні страви": "❄️",
    "сніданок": "🍳",
    "закуски": "🍢",
    "соуси": "🫙",
    "напій": "🍹"
};

/* ============================================
   CHEF UI ELEMENTS
   ============================================ */
const chefFab = document.getElementById("chefFab");
const chefChat = document.getElementById("chefChat");
const chefChatClose = document.getElementById("chefChatClose");
const chefChatMessages = document.getElementById("chefChatMessages");
const chefContextBubbles = document.getElementById("chefContextBubbles");
const chefUserInput = document.getElementById("chefUserInput");
const chefSendBtn = document.getElementById("chefSendBtn");

/* ============================================
   CHEF HELPERS
   ============================================ */

function toggleChefChat(open) {
    const shouldOpen = typeof open === "boolean" ? open : chefChat.classList.contains("is-hidden");
    if (shouldOpen) {
        chefChat.classList.remove("is-hidden");
    } else {
        chefChat.classList.add("is-hidden");
    }
}

function chefSay(text, options = {}) {
    const msg = document.createElement("div");
    msg.className = "chef-msg chef-msg--chef";
    msg.textContent = text;
    chefChatMessages.appendChild(msg);
    chefChatMessages.scrollTop = chefChatMessages.scrollHeight;
    
}

function userSay(text) {
    const msg = document.createElement("div");
    msg.className = "chef-msg chef-msg--user";
    msg.textContent = text;
    chefChatMessages.appendChild(msg);
    chefChatMessages.scrollTop = chefChatMessages.scrollHeight;
}

function setChefContextBubbles(bubbles) {
    chefContextBubbles.innerHTML = "";
    bubbles.forEach(b => {
        const btn = document.createElement("button");
        btn.className = "chef-context-bubble";
        btn.textContent = b.label;
        btn.addEventListener("click", () => b.onClick());
        chefContextBubbles.appendChild(btn);
    });
}
/* ============================================
   STICKY TIP — NEW SYSTEM
   ============================================ */
function chefSticky(text) {
    const container = document.getElementById("chefStickyContainer");

    const tip = document.createElement("div");
    tip.className = "chef-sticky-tip";
    tip.innerHTML = `
        <div class="chef-sticky-text">${text}</div>
        <button class="chef-sticky-close">×</button>
    `;

    container.appendChild(tip);

    // анімація появи
    setTimeout(() => tip.classList.add("show"), 10);

    // закриття по кліку
    tip.querySelector(".chef-sticky-close").addEventListener("click", () => {
        tip.classList.remove("show");
        setTimeout(() => tip.remove(), 250);
    });

    // авто-зникнення
    setTimeout(() => {
        tip.classList.remove("show");
        setTimeout(() => tip.remove(), 250);
    }, 12000);

    // обмеження кількості (макс 3)
    if (container.children.length > 3) {
        container.firstChild.remove();
    }
}

/* ============================================
   CHEF EVENTS
   ============================================ */

chefFab.addEventListener("click", () => {
    toggleChefChat(true);
    if (chefState.mode === "idle") {
        chefSay("Привіт! Я твій шеф‑наставник. Введи інгредієнти — разом щось вигадаємо 😉");
        chefState.mode = "intro";
    }
});

chefChatClose.addEventListener("click", () => toggleChefChat(false));

chefUserInput.addEventListener("keydown", e => {
    if (e.key === "Enter") chefSendBtn.click();
});


/* ============================================
   1) START FLOW — USER INPUT
   ============================================ */
async function startFlow() {
    document.getElementById("recipe-section").classList.add("hidden");

    const input = document.getElementById("ingredients").value;
    globalIngredients = input.split(",").map(i => i.trim()).filter(Boolean);

    if (globalIngredients.length === 0) return;
   
    const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients: globalIngredients })
    });

    const data = await response.json();
    globalKnown = data.known;

    showCategories(data.categories);

    // ChefPersona реакція
    chefState.mode = "categories";
    chefSay("Я вже бачу, що з цих інгредієнтів можна зробити кілька цікавих страв."); 
    chefSticky("Обери категорію — я підкажу далі.");
    setChefContextBubbles([
        {
            label: "Порадь щось швидке",
            onClick: () => chefSay("Для швидких страв обирай щось на кшталт закусок або простих гарячих страв.")
        },
        {
            label: "Щось легке",
            onClick: () => chefSay("Легкі страви часто ховаються в холодних закусках або салатах.")
        }
    ]);
}

/* ============================================
   2) SHOW CATEGORIES
   ============================================ */
function showCategories(categories) {
    const div = document.getElementById("categories");
    div.innerHTML = `<h2 class="section-title">Обери категорію:</h2>`;

    categories.forEach(cat => {
        const btn = document.createElement("div");
        const formatted = cat.charAt(0).toUpperCase() + cat.slice(1);

        btn.className = "category-btn";
        btn.innerHTML = `${categoryIcons[cat] || "🍽️"} ${formatted}`;
        btn.onclick = () => loadDishes(cat);

        div.appendChild(btn);
    });
}

/* ============================================
   3) LOAD DISHES
   ============================================ */
function loadDishes(category) {
    fetch("http://127.0.0.1:8000/dishes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            ingredients: globalIngredients,
            category: category
        })
    })
    .then(res => res.json())
    .then(data => {
        const div = document.getElementById("dishes");
        div.innerHTML = `<h2 class="section-title">Обери страву:</h2>`;

        data.dishes.forEach(dish => {
            const btn = document.createElement("div");
            btn.className = "dish-btn";
            btn.textContent = dish;
            btn.onclick = () => loadRecipe(dish);
            div.appendChild(btn);
        });

        // ChefPersona реакція
        chefState.mode = "dishes";
        chefSay("Гарний вибір категорії. Тепер обери страву.");
        chefSticky("Тепер обери страву — я підкажу, як її покращити.");
        setChefContextBubbles([
            {
                label: "Порадь найпростіше",
                onClick: () => chefSay("Обирай страву з коротшою назвою та менше екзотики — зазвичай вони простіші.")
            },
            {
                label: "Щось ефектне",
                onClick: () => chefSay("Для вау‑ефекту бери страву з запіканням або карамелізацією — виглядає завжди круто.")
            }
        ]);
    });
}

/* ============================================
   INGREDIENT ICONS
   ============================================ */
const ingredientIcons = {
    "курка": "🐔",
    "лимон": "🍋",
    "олія": "🛢️",
    "сіль": "🧂",
    "перець чорний": "🌶️",
    "часник": "🧄",
    "розмарин": "🌿",
    "мед": "🍯",
    "соєвий соус": "🥣",
    "перець": "🫑",
    "паприка": "🌶️",
    "апельсин": "🍊",
    "імбир": "🫚",
    "м'ята": "🌱",
    "ваніль": "🌼"
};

/* ============================================
   TILE RENDERERS
   ============================================ */
function renderIngredientTile(name, type = "default") {
    const icon = ingredientIcons[name];
    return `
        <span class="ingredient-tile tile-${type}" data-ing="${name}">
            ${icon ? icon : name}
        </span>
    `;
}

/* ============================================
   4) LOAD RECIPE
   ============================================ */
function loadRecipe(dish) {
    fetch("http://127.0.0.1:8000/recipe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            ingredients: globalIngredients,
            dish: dish
        })
    })
    .then(res => res.json())
    .then(data => {
        // оновлюємо глобальний стан для переходу в кухню
        window.currentIngredients = data.ingredients_available || [];

        const div = document.getElementById("recipe");
        // показуємо блок рецепта
        document.getElementById("recipe-section").classList.remove("hidden");

        // назва страви
        const formattedDish = data.dish.charAt(0).toUpperCase() + data.dish.slice(1);
        document.getElementById("recipe-title").innerText = `Рецепт: ${formattedDish}`;

        if (data.error) {
            div.innerHTML = `<p style="color: var(--kalyna)">${data.error}</p>`;
            return;
        }

        /* --- AVAILABLE INGREDIENTS --- */
        const availableHtml = data.ingredients_available.length
            ? data.ingredients_available.map(ing => {
                const pairs = data.pairings?.[ing] || [];
                return `
                    <div class="ingredient-item">
                        <div class="ingredient-header">
                            ${renderIngredientTile(ing, "available")}
                            <button class="toggle-arrow">⌄</button>
                        </div>
                        <div class="ingredient-panel">
                            <div class="pair-list">
                                ${pairs.map(p => renderIngredientTile(p, "pair")).join("")}
                            </div>
                        </div>
                    </div>
                `;
            }).join("")
            : "<span>Немає</span>";

        /* --- MISSING INGREDIENTS --- */
        const missingHtml = data.ingredients_missing.map(i => {
            const subs = data.substitutes[i] || [];
            return `
                <div class="ingredient-item">
                    <div class="ingredient-header">
                        ${renderIngredientTile(i, "missing")}
                        <button class="toggle-arrow">⌄</button>
                    </div>
                    <div class="ingredient-panel">
                        ${
                            subs.length
                                ? subs.map(s => renderIngredientTile(s, "substitute")).join("")
                                : `<div class="sub-block none">Немає замін</div>`
                        }
                    </div>
                </div>
            `;
        }).join("");

        /* --- REQUIRED INGREDIENTS --- */
        const requiredHtml = `
             <div class="ingredient-item required-block">
                <div class="ingredient-header">
                    <p class="required-title">Потрібні інгредієнти</p>
                    <button class="toggle-arrow">⌄</button>
                </div>
                <div class="ingredient-panel">
                    <div class="required-list">
                        ${data.ingredients_required
                            .map(ing => renderIngredientTile(ing, "required"))
                            .join("")}
                    </div>
                </div>
            </div>
        `;

        /* --- STEPS --- */
        const stepsHtml = data.steps.map(s => `<li>${s}</li>`).join("");

        /* --- INSERT INTO DOM --- */
        div.innerHTML = `
            ${requiredHtml}

            <div class="ing-columns">
                <div class="ing-col">
                    <p><b>Є у тебе:</b></p>
                    <div class="tag-container">${availableHtml}</div>
                </div>

                <div class="ing-col">
                    <p><b>Немає:</b></p>
                    <div class="tag-container">${missingHtml}</div>
                </div>
            </div>

            <p><b>Кроки:</b></p>
            <ol>${stepsHtml}</ol>
            <button id="continueWithChef" class="chef-btn">
            Продовжити з шефом
            </button>
        `;

        // Тепер кнопка існує — можна вішати обробник
    document.getElementById("continueWithChef").onclick = () => {
        const ingredients = getCurrentIngredients();
        localStorage.setItem("chef_ingredients", JSON.stringify(ingredients));
        window.location.href = "/kitchen/index.html";
    };

        /* ============================================
           INTERACTIONS
           ============================================ */

        /* --- CLICKABLE INGREDIENT TILES --- */
        document.querySelectorAll("[data-ing]").forEach(el => {
            el.addEventListener("click", event => {
                event.stopPropagation();
                fillSidePanel(el.getAttribute("data-ing"));
            });
        });

        /* --- ACCORDIONS --- */
        document.querySelectorAll(".ingredient-header").forEach(header => {
            const arrow = header.querySelector(".toggle-arrow");
            if (!arrow) return;

            arrow.addEventListener("click", event => {
                event.stopPropagation();
                const item = header.parentElement;

                document.querySelectorAll(".ingredient-item.open").forEach(openItem => {
                    if (openItem !== item) openItem.classList.remove("open");
                });

                item.classList.toggle("open");
            });
        });

        /* --- ChefPersona реакція на рецепт --- */
        chefState.mode = "recipe";
        chefState.lastDish = data.dish;
        chefSay(`Ось рецепт: ${formattedDish}.`);
        chefSticky("Хочеш зробити страву простішою або ефектнішою?");
        setChefContextBubbles([
            {
                label: "Зробити простішим",
                onClick: () => chefSay("Скороти кількість кроків і спецій — залиш базові, щоб не перевантажувати смак.")
            },
            {
                label: "Зробити ефектнішим",
                onClick: () => chefSay("Додай етап карамелізації або запікання — це завжди додає глибини смаку.")
            },
            {
                label: "Показати заміни",
                onClick: () => chefSay("Подивись на блок «Немає» — там я вже підготував заміни до відсутніх інгредієнтів.")
            }
        ]);
    });
}

/* ============================================
   SIDE PANEL LOGIC
   ============================================ */
const sidePanel = document.getElementById("sidePanel");
const sidePanelOverlay = sidePanel.querySelector(".side-panel-overlay");
const sidePanelClose = sidePanel.querySelector(".side-panel-close");

function openSidePanel() {
    sidePanel.classList.add("open");
}

function closeSidePanel() {
    sidePanel.classList.remove("open");
}

sidePanelOverlay.addEventListener("click", closeSidePanel);
sidePanelClose.addEventListener("click", closeSidePanel);

/* ============================================
   INGREDIENT INFO (TEMPORARY)
   ============================================ */
const ingredientInfo = {
    "курка": {
        description: "Курка — універсальний продукт, який добре поєднується з багатьма спеціями.",
        pairings: ["часник", "розмарин", "мед", "соєвий соус"]
    },
    "лимон": {
        description: "Лимон додає кислинку та свіжість.",
        pairings: ["курка", "імбир", "мед", "перець"]
    },
    "олія": {
        description: "Олія використовується для смаження та маринадів.",
        pairings: ["часник", "паприка"]
    },
    "сіль": {
        description: "Сіль підсилює смак страви.",
        pairings: ["перець", "олія"]
    },
    "часник": {
        description: "Часник додає пікантності та аромату.",
        pairings: ["курка", "олія", "паприка", "мед"]
    }
};

/* ============================================
   FILL SIDE PANEL
   ============================================ */
function fillSidePanel(ingredientName) {
    const titleEl = sidePanel.querySelector(".ingredient-title");
    const descEl = sidePanel.querySelector(".ingredient-description");
    const pairingGrid = sidePanel.querySelector(".pairing-grid");

    titleEl.textContent = ingredientName;
    pairingGrid.innerHTML = "";

    const info = ingredientInfo[ingredientName.toLowerCase()];

    if (!info) {
        descEl.textContent = "Інформація про цей інгредієнт поки недоступна.";
        openSidePanel();
        return;
    }

    descEl.textContent = info.description;

    info.pairings.forEach(pair => {
        const card = document.createElement("div");
        card.className = "pairing-card";
        card.textContent = pair;
        pairingGrid.appendChild(card);
    });

    chefSticky(`Добре поєднується з: ${info.pairings.join(", ")}`);

    openSidePanel();
}

/* ============================================
   CHAT WITH CHEF
   ============================================ */
async function sendChefMessage() {
    const input = document.getElementById("chefUserInput");
    const text = input.value.trim();
    if (!text) return;

    // Додаємо повідомлення користувача
    addChefMessage("user", text);
    input.value = "";

    // Відправляємо на сервер
    const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });

    const data = await res.json();

    // Додаємо відповідь шефа
    addChefMessage("chef", `${data.reply} <div class="state">[${data.state}]</div>`);
}

function addChefMessage(sender, text) {
    const container = document.getElementById("chefChatMessages");

    const div = document.createElement("div");
    div.className = sender === "chef" ? "chef-msg" : "user-msg";
    div.innerHTML = text;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Обробка кнопки
document.getElementById("chefSendBtn").onclick = sendChefMessage;

// Enter для відправки
document.getElementById("chefUserInput").addEventListener("keydown", e => {
    if (e.key === "Enter") sendChefMessage();
});

function getCurrentIngredients() {
    // Якщо у тебе вже є масив інгредієнтів — просто поверни його
    // Наприклад:
    return window.currentIngredients || [];

    // Якщо інгредієнти зберігаються в DOM — можна зчитати їх звідти
    // Але поки що цього не треба — достатньо першого варіанту
}
