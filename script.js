document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn = document.getElementById("analyzeBtn");
    const textInput = document.getElementById("inputText");
    const styleButtons = document.querySelectorAll(".style-btn");
    const riskButtons = document.querySelectorAll(".risk-btn");

    let selectedStyle = 1;

    /* -----------------------------------------
       STİL BUTONLARI
    ----------------------------------------- */
    styleButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            styleButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedStyle = parseInt(btn.dataset.style);
        });
    });

    /* -----------------------------------------
       ANALİZ ET
    ----------------------------------------- */
    analyzeBtn.addEventListener("click", () => {
        const text = textInput.value.trim();
        if (!text) return alert("Lütfen bir metin girin.");

        analyzeBtn.classList.add("shake");
        setTimeout(() => analyzeBtn.classList.remove("shake"), 300);

        riskButtons.forEach(btn => {
            btn.style.transform = "scale(1.05)";
            setTimeout(() => btn.style.transform = "scale(1)", 150);
        });

        // 🔥 LOCALHOST GİTTİ → RENDER BACKEND GELDİ
        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, style: selectedStyle })
        })
            .then(r => r.json())
            .then(data => renderResults(data))
            .catch(err => {
                console.error("FETCH ERROR:", err);
                alert("Sunucuya bağlanılamadı. Backend çalışmıyor olabilir.");
            });
    });

    /* -----------------------------------------
       SONUÇLARI ÇİZ
    ----------------------------------------- */
    function renderResults(data) {

        const lowPanel = document.getElementById("panel-low");
        const midPanel = document.getElementById("panel-medium");
        const highPanel = document.getElementById("panel-high");

        lowPanel.innerHTML = "";
        midPanel.innerHTML = "";
        highPanel.innerHTML = "";

        let counts = { low: 0, medium: 0, high: 0 };

        data.pairs.forEach(pair => {

            const box = document.createElement("div");
            box.classList.add("pair-box");

            if (pair.severity === "1") box.classList.add("pair-box-low");
            else if (pair.severity === "2") box.classList.add("pair-box-medium");
            else box.classList.add("pair-box-high");

            const title = document.createElement("div");
            title.classList.add("pair-title");
            title.innerText = `Etkileşim : ${pair.drug_1} + ${pair.drug_2}`;

            const content = document.createElement("div");
            content.classList.add("pair-content");
            content.innerHTML = pair.explanation;

            title.addEventListener("click", () => {
                content.classList.toggle("open");

                const parentPanel = box.parentElement;
                setTimeout(() => {
                    parentPanel.style.maxHeight = parentPanel.scrollHeight + "px";
                }, 200);
            });

            box.appendChild(title);
            box.appendChild(content);

            if (pair.severity === "1") { lowPanel.appendChild(box); counts.low++; }
            else if (pair.severity === "2") { midPanel.appendChild(box); counts.medium++; }
            else { highPanel.appendChild(box); counts.high++; }
        });

        document.getElementById("low-count").innerText = counts.low;
        document.getElementById("medium-count").innerText = counts.medium;
        document.getElementById("high-count").innerText = counts.high;
    }

    /* -----------------------------------------
       PANEL AÇ/KAPA
    ----------------------------------------- */
    const riskPanels = {
        low: document.getElementById("panel-low"),
        medium: document.getElementById("panel-medium"),
        high: document.getElementById("panel-high")
    };

    riskButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const target = btn.dataset.target;

            Object.values(riskPanels).forEach(panel => {
                panel.classList.remove("open");
                panel.style.maxHeight = "0px";
            });

            riskButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const activePanel = riskPanels[target];
            activePanel.classList.add("open");

            setTimeout(() => {
                activePanel.style.maxHeight = activePanel.scrollHeight + "px";
            }, 150);
        });
    });

});
