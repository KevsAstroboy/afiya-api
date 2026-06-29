## ADDED Requirements

### Requirement: Pluggable LLM provider interface
The system SHALL define an `LLMProvider` abstract class with a `generate(prompt, model, max_tokens) -> str` method. New LLM providers SHALL be addable by implementing this interface without modifying the workflow engine core.

#### Scenario: Generate text via provider interface
- **WHEN** `provider.generate("Hello world", "model-name", 500)` is called
- **THEN** the provider SHALL return the LLM's response text

#### Scenario: Provider raises exception on API error
- **WHEN** the underlying API call fails (network error, rate limit, auth error)
- **THEN** the exception SHALL propagate to the caller wrapped in a descriptive error

### Requirement: Anthropic provider implementation
The system SHALL provide an `AnthropicProvider` implementing `LLMProvider` using the `anthropic` Python SDK. It SHALL be selected when `LLM_PROVIDER=anthropic`.

#### Scenario: Anthropic generate with Claude model
- **WHEN** `AnthropicProvider` is called with model `claude-sonnet-4-20250514`
- **THEN** the `anthropic.Anthropic().messages.create()` method SHALL be invoked with the prompt, model, and max_tokens

#### Scenario: Anthropic provider initialized from config
- **WHEN** `ANTHROPIC_API_KEY` is set in environment
- **THEN** the provider SHALL authenticate with that key

### Requirement: OpenAI provider implementation
The system SHALL provide an `OpenAIProvider` implementing `LLMProvider` using the `openai` Python SDK (async client). It SHALL be selected when `LLM_PROVIDER=openai`.

#### Scenario: OpenAI generate with GPT model
- **WHEN** `OpenAIProvider` is called with model `gpt-4o`
- **THEN** the `openai.AsyncOpenAI().chat.completions.create()` method SHALL be invoked

#### Scenario: OpenAI provider initialized from config
- **WHEN** `OPENAI_API_KEY` is set in environment
- **THEN** the provider SHALL authenticate with that key

### Requirement: LLM provider factory based on configuration
The system SHALL provide an `LLMProviderFactory` that returns the correct provider instance based on the `LLM_PROVIDER` configuration value.

#### Scenario: Factory returns Anthropic provider
- **WHEN** `LLM_PROVIDER=anthropic` is configured
- **THEN** `LLMProviderFactory.create()` SHALL return an `AnthropicProvider` instance

#### Scenario: Factory returns OpenAI provider
- **WHEN** `LLM_PROVIDER=openai` is configured
- **THEN** `LLMProviderFactory.create()` SHALL return an `OpenAIProvider` instance

#### Scenario: Unknown provider configuration
- **WHEN** `LLM_PROVIDER=unknown` is configured
- **THEN** `LLMProviderFactory.create()` SHALL raise a clear configuration error

### Requirement: LLM prompt template variable substitution
The workflow engine's `LLMHandler` SHALL substitute `{variable_name}` placeholders in the prompt template with corresponding values from the workflow context using Python's `str.format_map()`.

#### Scenario: Single variable substitution
- **WHEN** prompt is `"Patient: {input_nom}"` and context has `input_nom = "Koné"`
- **THEN** the LLM SHALL receive the prompt `"Patient: Koné"`

#### Scenario: Multiple variable substitution
- **WHEN** prompt is `"Montant: {db_payment_record[amount]} FCFA | Patient: {input_prenom} {input_nom}"`
- **THEN** all variables SHALL be resolved from the context before sending to the LLM

#### Scenario: Nested dict access in substitution
- **WHEN** prompt uses `{db_payment_record[montant]}` and the context has a nested dict
- **THEN** the value SHALL be correctly extracted from the nested dict

### Requirement: LLM response auto-casting
The `LLMHandler` SHALL attempt to cast the LLM's response text to `float` if it represents a number. If casting fails, the response SHALL remain as a string.

#### Scenario: Numeric response cast to float
- **WHEN** the LLM returns `"0.75"`
- **THEN** the step output SHALL be the float `0.75`

#### Scenario: Non-numeric response stays as string
- **WHEN** the LLM returns `"Bonjour, votre paiement est confirmé"`
- **THEN** the step output SHALL be the string `"Bonjour, votre paiement est confirmé"`

### Requirement: LLM handler reports errors without crashing the workflow
When an LLM API call fails (network error, timeout, rate limit), the `LLMHandler` SHALL return a FAILURE `StepResult` with the error message, and the workflow engine SHALL route to the failure branch.

#### Scenario: LLM API timeout handled gracefully
- **WHEN** the LLM API call times out
- **THEN** the step SHALL return status FAILURE with error `"LLM API timeout"` and the workflow SHALL continue to the `on_failure_step_id`
