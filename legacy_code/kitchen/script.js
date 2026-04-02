/* BASIC UI */
function chefSay(text) {
    const el = document.getElementById("chef-text");
    el.style.opacity = 0;

    setTimeout(() => {
        el.innerHTML = text;
        el.style.opacity = 1;
    }, 150);
}

/* CONTEXT BUTTONS */
function setChefButtons(buttons) {
    const container = document.getElementById("chef-buttons");
    container.innerHTML = "";

    buttons.forEach(b => {
        const btn = document.createElement("button");
        btn.textContent = b.label;
        btn.onclick = b.onClick;
        container.appendChild(btn);
    });
}

document.getElementById("backToMain").onclick = () => {
    window.location.href = "/web/index.html";
};

/* BUBBLES */
function chefBubble(text) {
    const container = document.getElementById("chef-bubbles-container");

    const bubble = document.createElement("div");
    bubble.className = "chef-bubble-small";
    bubble.innerHTML = text;
    
    // хаотичний нахил
    const tilt = (Math.random() * 6 - 3).toFixed(1); // від -3 до +3 градусів
    bubble.style.transform = `translateY(10px) scale(0.95) rotate(${tilt}deg)`;

    container.appendChild(bubble);

    setTimeout(() => bubble.classList.add("show"), 10);

    setTimeout(() => {
        bubble.classList.remove("show");
        setTimeout(() => bubble.remove(), 300);
    }, 3000);
}

/* MAIN LOGIC */
window.onload = () => {
    const raw = localStorage.getItem("chef_ingredients");
    let ingredients = [];

    if (raw) {
        try { ingredients = JSON.parse(raw); }
        catch { ingredients = []; }
    }

    if (!ingredients.length) {
        chefSay("Почнемо з нуля. Я вже на кухні.");
        return;
    }

    chefSay(`Бачу інгредієнти: <b>${ingredients.join(", ")}</b>. Давай продовжимо.`);

    if (ingredients.includes("лимон")) chefReact("flavor");
    if (ingredients.includes("гриб")) chefReact("thinking");
    if (ingredients.includes("томат")) chefReact("excited");

    setChefButtons([
    {
        label: "Що приготувати?",
        onClick: () => {
            chefReact("thinking");
            chefAsk("Що приготувати з цих інгредієнтів?", ingredients);
        }
    },
    {
        label: "Простий варіант",
        onClick: () => {
            chefReact("excited");
            chefAsk("Дай простий варіант", ingredients);
        }
    },
    {
        label: "Ефектний варіант",
        onClick: () => {
            chefReact("chaotic");
            chefAsk("Дай ефектний варіант", ingredients);
        }
    },
    {
        label: "Що додати?",
        onClick: () => {
            chefReact("flavor");
            chefAsk("Що додати для кращого смаку?", ingredients);
        }
    }
    ]);
};

/* AI REQUEST */
async function chefAsk(message, ingredients) {
    const res = await fetch("http://127.0.0.1:8000/chef", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message, ingredients })
    });

    const data = await res.json();
    console.log("AI reply:", data);

    setTimeout(() => {
        chefBubble("Готую відповідь...");
    }, 999);
    chefSay(data.reply || data.answer || data.message || "Порожня відповідь");
    if ((data.reply || "").length > 200) {
        chefReact("thinking");
    }
}

const chefReactions = {
    thinking: [
        "Гм… дай секунду, я вже нюхаю аромат майбутньої страви.",
        "Ооо, цікаво… мозок шефа запускає турборежим.",
        "Так-так, я вже уявляю смак…",
        "Зараз буде щось смачне, відчуваю це всім серцем."
    ],
    excited: [
        "О, це буде бомба!",
        "Так! Оце я люблю!",
        "Ооо, це вже цікаво!",
        "Чудовий вибір, я вже в передчутті!"
    ],
    flavor: [
        "Це як симфонія ароматів у кожній ложці.",
        "Тут потрібен баланс — солодке, кисле, солоне, умамі.",
        "О, цей інгредієнт — справжній герой смаку!",
        "Трохи кислинки — і страва оживе."
    ],
    chaotic: [
        "Ооо, я знаю! Зробимо щось таке, що навіть бабуся здивується!",
        "Ха! Це буде магія на кухні!",
        "Зараз буде експеримент… але смачний!",
        "Я відчуваю натхнення, як після запаху свіжого хліба!"
    ],
    error: [
        "Ой, щось пішло не так… але я впораюсь!",
        "Хм, це дивно… але ми знайдемо рішення.",
        "Не хвилюйся, шеф усе владнає.",
        "Техніка інколи бавиться, але я — ні!"
    ]
};

function chefReact(type) {
    const list = chefReactions[type];
    if (!list) return;
    const text = list[Math.floor(Math.random() * list.length)];
    chefBubble(text);
}