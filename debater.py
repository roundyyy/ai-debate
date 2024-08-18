import multiprocessing
import nltk
import requests
import json
import os
from RealtimeTTS import TextToAudioStream, CoquiEngine
import asyncio
import tkinter as tk
from tkinter import scrolledtext, ttk
from threading import Thread
import httpx

CONVERSATION_LOG = "conversation_log.txt"


class DebateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Debate App")

        # Apply Improved Dark Mode
        self.root.configure(bg="#1e1e1e")
        self.default_bg = "#1e1e1e"
        self.default_fg = "#dcdcdc"
        self.entry_bg = "#2d2d30"
        self.entry_fg = "#ffffff"
        self.highlight_bg = "#3e3e42"

        # Create or reset conversation log file with UTF-8 encoding
        self.reset_conversation_log()

        # Fetch available models
        self.models = self.get_ollama_models()

        # Topic entry field
        self.topic_label = tk.Label(
            self.root,
            text="Enter Debate Topic (or Thesis):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.topic_label.pack()

        self.topic_entry = tk.Entry(
            self.root, width=200, bg=self.entry_bg, fg=self.entry_fg
        )
        self.topic_entry.pack()

        # GUI layout
        self.pro_frame = tk.Frame(self.root, bg=self.default_bg)
        self.con_frame = tk.Frame(self.root, bg=self.default_bg)

        self.pro_frame.pack(side="left", fill="both", expand=True)
        self.con_frame.pack(side="right", fill="both", expand=True)

        # Model selection dropdowns for Debater 1 (Pro)
        self.pro_model_var = tk.StringVar()
        self.pro_model_var.set(self.models[0])  # Set default model
        self.pro_model_label = tk.Label(
            self.pro_frame,
            text="Select Model for Debater 1 (Pro):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.pro_model_label.pack()
        self.pro_model_dropdown = ttk.Combobox(
            self.pro_frame, textvariable=self.pro_model_var, values=self.models
        )
        self.pro_model_dropdown.pack()

        # Checkbox for "Unmannered" option for Debater 1
        self.pro_unmannered_var = tk.BooleanVar()
        self.pro_unmannered_checkbox = tk.Checkbutton(
            self.pro_frame,
            text="Unmannered",
            variable=self.pro_unmannered_var,
            bg=self.default_bg,
            fg=self.default_fg,
            selectcolor=self.highlight_bg,
        )
        self.pro_unmannered_checkbox.pack()

        # Checkbox for "Rhymes & Verses" option for Debater 1
        self.pro_rap_var = tk.BooleanVar()
        self.pro_rap_checkbox = tk.Checkbutton(
            self.pro_frame,
            text="Rhymes & Verses",
            variable=self.pro_rap_var,
            bg=self.default_bg,
            fg=self.default_fg,
            selectcolor=self.highlight_bg,
        )
        self.pro_rap_checkbox.pack()

        # Entry for response length for Debater 1
        self.pro_length_label = tk.Label(
            self.pro_frame,
            text="Response Length (words):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.pro_length_label.pack()
        self.pro_length_entry = tk.Entry(
            self.pro_frame, width=10, bg=self.entry_bg, fg=self.entry_fg
        )
        self.pro_length_entry.insert(0, "50")
        self.pro_length_entry.pack()

        # Model selection dropdowns for Debater 2 (Con)
        self.con_model_var = tk.StringVar()
        self.con_model_var.set(self.models[0])  # Set default model
        self.con_model_label = tk.Label(
            self.con_frame,
            text="Select Model for Debater 2 (Con):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.con_model_label.pack()
        self.con_model_dropdown = ttk.Combobox(
            self.con_frame, textvariable=self.con_model_var, values=self.models
        )
        self.con_model_dropdown.pack()

        # Checkbox for "Unmannered" option for Debater 2
        self.con_unmannered_var = tk.BooleanVar()
        self.con_unmannered_checkbox = tk.Checkbutton(
            self.con_frame,
            text="Unmannered",
            variable=self.con_unmannered_var,
            bg=self.default_bg,
            fg=self.default_fg,
            selectcolor=self.highlight_bg,
        )
        self.con_unmannered_checkbox.pack()

        # Checkbox for "Rhymes & Verses" option for Debater 2
        self.con_rap_var = tk.BooleanVar()
        self.con_rap_checkbox = tk.Checkbutton(
            self.con_frame,
            text="Rhymes & Verses",
            variable=self.con_rap_var,
            bg=self.default_bg,
            fg=self.default_fg,
            selectcolor=self.highlight_bg,
        )
        self.con_rap_checkbox.pack()

        # Entry for response length for Debater 2
        self.con_length_label = tk.Label(
            self.con_frame,
            text="Response Length (words):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.con_length_label.pack()
        self.con_length_entry = tk.Entry(
            self.con_frame, width=10, bg=self.entry_bg, fg=self.entry_fg
        )
        self.con_length_entry.insert(0, "50")
        self.con_length_entry.pack()

        # Text display areas
        self.pro_label = tk.Label(
            self.pro_frame,
            text="Debater 1 (Pro):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.pro_label.pack()

        self.pro_text = scrolledtext.ScrolledText(
            self.pro_frame,
            wrap=tk.WORD,
            height=20,
            bg="gray25",
            fg=self.entry_fg,
            insertbackground=self.entry_fg,
        )
        self.pro_text.pack(expand=True, fill="both")

        self.con_label = tk.Label(
            self.con_frame,
            text="Debater 2 (Con):",
            bg=self.default_bg,
            fg=self.default_fg,
        )
        self.con_label.pack()

        self.con_text = scrolledtext.ScrolledText(
            self.con_frame,
            wrap=tk.WORD,
            height=20,
            bg="gray25",
            fg=self.entry_fg,
            insertbackground=self.entry_fg,
        )
        self.con_text.pack(expand=True, fill="both")

        self.start_button = tk.Button(
            self.root,
            text="Start",
            command=self.start_debate,
            bg=self.highlight_bg,
            fg=self.default_fg,
        )
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = tk.Button(
            self.root,
            text="Reset",
            command=self.stop_debate,
            bg=self.highlight_bg,
            fg=self.default_fg,
        )
        self.stop_button.pack(side="right", padx=10, pady=10)

        self.running = False
        self.turn = 1
        self.conversation = ""
        self.is_playing = False
        self.next_prompt = ""
        self.loop = asyncio.new_event_loop()

    def get_ollama_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                return model_names
            else:
                print(
                    f"Failed to fetch Ollama models. Status code: {response.status_code}"
                )
                return []
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    async def get_ollama_response(self, model, prompt):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "keep_alive": 0, "prompt": prompt},
                    timeout=None,
                )
                response.raise_for_status()
                generated_text = ""
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            generated_text += data["response"]
                return generated_text
        except Exception as e:
            print(f"Error during Ollama request: {e}")
            return None

    def speak_text(self, text):
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            self.audio_stream.feed(sentence)
            self.audio_stream.play()

    def reset_event_loop(self):
        # Check if the loop is still running and stop it
        if self.loop.is_running():
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            self.loop.call_soon_threadsafe(self.loop.stop)

        # Close the loop if it hasn't been closed
        if not self.loop.is_closed():
            self.loop.close()

        # Create a new event loop for the next time the debate is started
        self.loop = asyncio.new_event_loop()

    def start_debate(self):
        # Reset the event loop without resetting the state
        self.reset_event_loop()

        self.topic = self.topic_entry.get()
        self.conversation = f"Topic: {self.topic}\n\n"

        # Set the initial prompt for Debater 1 (Pro) - purely supportive
        self.prompt1 = (
            f"Debater 1 (Pro): Argue in favor of the topic '{self.topic}'. "
            f"Provide a clear, concise argument in about {self.pro_length_entry.get()} words."
        )

        self.running = True
        self.tts_engine = CoquiEngine()
        self.audio_stream = TextToAudioStream(
            self.tts_engine,
            on_audio_stream_stop=self.on_playback_finished,
            language="en",
        )
        # Start the event loop in a separate thread
        self.debate_thread = Thread(target=self.start_event_loop)
        self.debate_thread.start()

    def update_prompts(self):
        rap_instruction = "Respond using rhymes and verses like in a rap song. Make sure you finish verse lines with commas or dots (, .)."

        # Retrieve word lengths
        pro_word_length = self.pro_length_entry.get()
        con_word_length = self.con_length_entry.get()

        # Read the full conversation log, if available
        with open(CONVERSATION_LOG, "r", encoding="utf-8") as f:
            full_conversation = f.read()

        # Get the last statement from the conversation log, or set it to the topic if it's the first turn
        last_statement = (
            self.conversation.splitlines()[-1]
            if len(self.conversation.splitlines()) > 1
            else self.topic
        )

        # Check if Debater 1 should be unmannered or use rap instructions
        pro_mannered = (
            "Act for fun like you are very rude.You are allowed to curse."
            if self.pro_unmannered_var.get()
            else ""
        )
        pro_rap = rap_instruction if self.pro_rap_var.get() else ""

        # Debater 1 (Pro) - Always supports the topic
        self.prompt1 = (
            f"Provide a concise argument supporting the statement: '{self.topic}'."
            f"Focus solely on the argument itself, without additional commentary, countering the following argument: '{last_statement}'."
            f" {pro_mannered} {pro_rap} Limit your response to {pro_word_length} words."
            f"\n\nConversation log:\n{full_conversation}"
        )

        # Check if Debater 2 should be unmannered or use rap instructions
        con_mannered = (
            "Act for fun like you are very rude.You are allowed to curse."
            if self.con_unmannered_var.get()
            else ""
        )
        con_rap = rap_instruction if self.con_rap_var.get() else ""

        # Debater 2 (Con) - Always opposes the topic
        self.prompt2 = (
            f"Provide a concise argument opposing the statement: '{self.topic}'."
            f"Focus solely on the argument itself, without additional commentary, countering the following argument: '{last_statement}'."
            f" {con_mannered} {con_rap} Limit your response to {con_word_length} words."
            f"\n\nConversation log:\n{full_conversation}"
        )

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.debate_loop())

    def stop_debate(self):
        self.running = False

        if self.loop.is_running():
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            self.loop.call_soon_threadsafe(self.loop.stop)

        self.root.after(100, self.check_thread_completion)

    def check_thread_completion(self):
        if self.debate_thread.is_alive():
            # If the thread is still running, check again after a delay
            self.root.after(100, self.check_thread_completion)
        else:
            # Once the thread has finished, reset the state and close the loop
            self.reset_state()

            if not self.loop.is_closed():
                self.loop.close()  # Ensure the loop is closed

            # Create a new loop for the next time the debate is started
            self.loop = asyncio.new_event_loop()

    def reset_state(self):
        # Resetting all the relevant attributes
        self.turn = 1
        self.conversation = ""
        self.is_playing = False
        self.next_prompt = ""
        self.running = False  # Ensure running is set to False

        # Clear the text areas
        self.pro_text.delete(1.0, tk.END)
        self.con_text.delete(1.0, tk.END)

        # Reset conversation log file
        if os.path.exists(CONVERSATION_LOG):
            os.remove(CONVERSATION_LOG)
        with open(CONVERSATION_LOG, "w", encoding="utf-8") as f:
            f.write("Debate Conversation Log\n\n")

        # Reset the topic entry field
        self.topic_entry.delete(0, tk.END)

        # Reset the selected models and checkboxes
        self.pro_model_var.set(self.models[0])
        self.con_model_var.set(self.models[0])
        self.pro_unmannered_var.set(False)
        self.pro_rap_var.set(False)
        self.con_unmannered_var.set(False)
        self.con_rap_var.set(False)

        # Reset the response lengths
        self.pro_length_entry.delete(0, tk.END)
        self.pro_length_entry.insert(0, "50")
        self.con_length_entry.delete(0, tk.END)
        self.con_length_entry.insert(0, "50")

    async def debate_loop(self):
        try:
            while self.running:
                self.update_prompts()  # Ensure prompts are updated each loop

                if self.turn % 2 == 1:
                    self.pro_text.delete(1.0, tk.END)
                    self.pro_text.insert(tk.END, "\nDebater 1 (Pro):\n")
                    selected_model = self.pro_model_var.get()

                    # Preload next response while the current one is speaking
                    next_response_task = asyncio.create_task(
                        self.get_ollama_response(self.con_model_var.get(), self.prompt2)
                    )

                    response = await self.get_ollama_response(
                        selected_model, self.prompt1
                    )
                    if response:
                        self.conversation += f"Debater 1 (Pro): {response}\n\n"
                        with open(CONVERSATION_LOG, "a", encoding="utf-8") as f:
                            f.write(f"Debater 1 (Pro): {response}\n\n")
                        self.pro_text.insert(tk.END, response)
                        self.is_playing = True

                        self.speak_text(response)

                        # Wait for the next response to be ready
                        await next_response_task

                        # Prepare next prompt based on the response
                        self.next_prompt = f"Debater 1 (Pro) argued: '{response}'. Consider the entire conversation so far, but respond only to this argument. Provide a compelling counterargument in about {self.pro_length_entry.get()} words."

                        # Retrieve the preloaded response for the next turn
                        response = await next_response_task

                else:
                    self.con_text.delete(1.0, tk.END)
                    self.con_text.insert(tk.END, "\nDebater 2 (Con):\n")
                    selected_model = self.con_model_var.get()

                    # Preload next response while the current one is speaking
                    next_response_task = asyncio.create_task(
                        self.get_ollama_response(self.pro_model_var.get(), self.prompt1)
                    )

                    response = await self.get_ollama_response(
                        selected_model, self.prompt2
                    )
                    if response:
                        self.conversation += f"Debater 2 (Con): {response}\n\n"
                        with open(CONVERSATION_LOG, "a", encoding="utf-8") as f:
                            f.write(f"Debater 2 (Con): {response}\n\n")
                        self.con_text.insert(tk.END, response)
                        self.is_playing = True

                        self.speak_text(response)

                        # Wait for the next response to be ready
                        await next_response_task

                        # Prepare next prompt based on the response
                        self.next_prompt = f"Debater 2 (Con) argued: '{response}'. Consider the entire conversation so far, but respond only to this argument. Strengthen your position on the topic: '{self.topic}' in about {self.con_length_entry.get()} words."

                        # Retrieve the preloaded response for the next turn
                        response = await next_response_task

                while self.is_playing:
                    await asyncio.sleep(0.1)

                if self.turn % 2 == 1:
                    self.prompt2 = f"{self.conversation}{self.next_prompt}"
                else:
                    self.prompt1 = f"{self.conversation}{self.next_prompt}"

                self.turn += 1
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            # Handle the cancellation gracefully, if needed
            print("Debate loop was cancelled.")
        finally:
            # Any cleanup code that needs to be run when the loop ends
            print("Debate loop has been terminated.")

    def on_playback_finished(self):
        self.is_playing = False
        if self.running:
            asyncio.run_coroutine_threadsafe(self.play_next(), self.loop)

    async def play_next(self):
        pass  # Placeholder for additional logic if needed

    def reset_conversation_log(self):

        if os.path.exists(CONVERSATION_LOG):
            os.remove(CONVERSATION_LOG)
        with open(CONVERSATION_LOG, "w", encoding="utf-8") as f:
            f.write("Debate Conversation Log\n\n")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    nltk.download("punkt", quiet=True)

    root = tk.Tk()
    app = DebateApp(root)
    root.mainloop()
