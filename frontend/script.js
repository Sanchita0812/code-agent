class AICodeAgent {
    constructor() {
        this.apiUrl = `${window.location.origin}/code/prompt_on_repo`;
        this.responseContainer = document.getElementById('agent-response');
        this.form = document.getElementById('repo-form');
        this.submitBtn = document.getElementById('submitBtn');
        this.repoInput = document.getElementById('repo-url');
        this.promptInput = document.getElementById('prompt');

        this.bindEvents();
        this.prefillFromURL();
    }

    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    prefillFromURL() {
        const params = new URLSearchParams(window.location.search);
        const repo = params.get('repo-url');
        const prompt = params.get('prompt');
        if (repo) this.repoInput.value = decodeURIComponent(repo);
        if (prompt) this.promptInput.value = decodeURIComponent(prompt);
        if (repo && prompt) this.form.requestSubmit();
    }

    async handleSubmit(e) {
        e.preventDefault();
        const repoUrl = this.repoInput.value.trim();
        const prompt = this.promptInput.value.trim();

        if (!repoUrl || !prompt) {
            this.showResponse('❌ Please enter both a valid repo URL and prompt.');
            return;
        }

        this.submitBtn.disabled = true;
        this.showResponse('⏳ Running AI Agent...');

        try {
            const res = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repoUrl, prompt })
            });

            if (!res.ok) throw new Error(`Error: ${res.status}`);
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        const msg = line.replace('data:', '').trim();
                        this.appendToResponse(`📝 ${msg}`);
                    }
                }
            }
        } catch (err) {
            this.appendToResponse(`❌ Error: ${err.message}`);
        } finally {
            this.submitBtn.disabled = false;
        }
    }

    showResponse(message) {
        this.responseContainer.innerHTML = `<div>${message}</div>`;
    }

    appendToResponse(message) {
        const div = document.createElement('div');
        div.textContent = message;
        this.responseContainer.appendChild(div);
        this.responseContainer.scrollTop = this.responseContainer.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => new AICodeAgent());
