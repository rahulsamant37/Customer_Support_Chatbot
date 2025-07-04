import pytest
import sys
import os

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_library.prompt import PROMPT_TEMPLATES

class TestPromptTemplates:
    """Test cases for prompt templates."""
    
    def test_prompt_templates_exists(self):
        """Test that PROMPT_TEMPLATES is defined and accessible."""
        assert PROMPT_TEMPLATES is not None
        assert isinstance(PROMPT_TEMPLATES, dict)
    
    def test_product_bot_template_exists(self):
        """Test that the product_bot template exists."""
        assert "product_bot" in PROMPT_TEMPLATES
        assert isinstance(PROMPT_TEMPLATES["product_bot"], str)
        assert len(PROMPT_TEMPLATES["product_bot"]) > 0
    
    def test_product_bot_template_structure(self):
        """Test the structure and content of the product_bot template."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        # Check for required placeholders
        assert "{context}" in template
        assert "{question}" in template
        
        # Check for key instruction elements
        assert "EcommerceBot" in template
        assert "product recommendations" in template
        assert "customer queries" in template
        
        # Check for important instructions
        assert "context is empty" in template.lower() or "no relevant product information" in template.lower()
        assert "concise" in template or "informative" in template
    
    def test_template_formatting(self):
        """Test that templates can be formatted with sample data."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        # Test formatting with sample data
        sample_context = "Product: Test Headphones\nRating: 5 stars\nReview: Great sound quality"
        sample_question = "Tell me about these headphones"
        
        try:
            formatted_template = template.format(
                context=sample_context,
                question=sample_question
            )
            
            assert sample_context in formatted_template
            assert sample_question in formatted_template
            assert "{context}" not in formatted_template  # Should be replaced
            assert "{question}" not in formatted_template  # Should be replaced
        except KeyError as e:
            pytest.fail(f"Template formatting failed due to missing placeholder: {e}")
    
    def test_template_with_empty_context(self):
        """Test template formatting with empty context."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        formatted_template = template.format(
            context="",
            question="What products do you recommend?"
        )
        
        assert "What products do you recommend?" in formatted_template
        assert "{context}" not in formatted_template
        assert "{question}" not in formatted_template
    
    def test_template_with_special_characters(self):
        """Test template formatting with special characters in inputs."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        special_context = "Product: Headphones with \"quotes\" & special chars 🎧"
        special_question = "What about this product's price & availability?"
        
        formatted_template = template.format(
            context=special_context,
            question=special_question
        )
        
        assert special_context in formatted_template
        assert special_question in formatted_template
    
    def test_template_length_reasonable(self):
        """Test that the template length is reasonable for an AI prompt."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        # Template should be comprehensive but not excessively long
        assert len(template) > 100  # Should have substantial content
        assert len(template) < 2000  # Should not be excessively long
    
    def test_template_contains_key_instructions(self):
        """Test that the template contains key instructions for the AI."""
        template = PROMPT_TEMPLATES["product_bot"]
        
        # Check for important behavioral instructions
        key_phrases = [
            "analyze",
            "product",
            "rating",
            "review",
            "accurate",
            "helpful",
            "relevant"
        ]
        
        template_lower = template.lower()
        for phrase in key_phrases:
            assert phrase in template_lower, f"Template should contain '{phrase}'"

class TestPromptTemplateExtensibility:
    """Test the extensibility and structure of the prompt template system."""
    
    def test_template_dictionary_structure(self):
        """Test that the template system is properly structured for extension."""
        assert isinstance(PROMPT_TEMPLATES, dict)
        
        # Each template should be a string
        for key, value in PROMPT_TEMPLATES.items():
            assert isinstance(key, str), f"Template key '{key}' should be a string"
            assert isinstance(value, str), f"Template value for '{key}' should be a string"
            assert len(value) > 0, f"Template '{key}' should not be empty"
    
    def test_add_new_template(self):
        """Test that new templates can be added to the system."""
        # Save original state
        original_templates = PROMPT_TEMPLATES.copy()
        
        try:
            # Add a new template
            test_template = "Test template with {placeholder}"
            PROMPT_TEMPLATES["test_template"] = test_template
            
            assert "test_template" in PROMPT_TEMPLATES
            assert PROMPT_TEMPLATES["test_template"] == test_template
            
            # Test that it can be formatted
            formatted = PROMPT_TEMPLATES["test_template"].format(placeholder="test value")
            assert "test value" in formatted
            
        finally:
            # Restore original state
            PROMPT_TEMPLATES.clear()
            PROMPT_TEMPLATES.update(original_templates)
    
    def test_template_naming_convention(self):
        """Test that template names follow a consistent convention."""
        for template_name in PROMPT_TEMPLATES.keys():
            # Should be lowercase with underscores
            assert template_name.islower(), f"Template name '{template_name}' should be lowercase"
            assert " " not in template_name, f"Template name '{template_name}' should not contain spaces"
            
            # Should use underscores for word separation
            if "_" in template_name:
                parts = template_name.split("_")
                for part in parts:
                    assert part.isalpha() or part.isalnum(), f"Template name part '{part}' should be alphanumeric"

class TestPromptTemplateValidation:
    """Test validation of prompt templates."""
    
    def test_template_placeholder_consistency(self):
        """Test that all templates use consistent placeholder naming."""
        for template_name, template in PROMPT_TEMPLATES.items():
            # Find all placeholders in the template
            import re
            placeholders = re.findall(r'\{([^}]+)\}', template)
            
            # Check that placeholders use consistent naming
            for placeholder in placeholders:
                assert placeholder.islower(), f"Placeholder '{placeholder}' in template '{template_name}' should be lowercase"
                assert "_" not in placeholder or placeholder.replace("_", "").isalnum(), f"Placeholder '{placeholder}' should use valid naming"
    
    def test_template_no_syntax_errors(self):
        """Test that templates don't have Python string formatting syntax errors."""
        for template_name, template in PROMPT_TEMPLATES.items():
            try:
                # Try to find all format fields
                import string
                formatter = string.Formatter()
                fields = list(formatter.parse(template))
                
                # Each field should be properly formatted
                for literal_text, field_name, format_spec, conversion in fields:
                    if field_name is not None:
                        assert field_name != "", f"Template '{template_name}' has empty field name"
                        
            except ValueError as e:
                pytest.fail(f"Template '{template_name}' has formatting syntax error: {e}")
    
    def test_template_required_placeholders(self):
        """Test that product_bot template has all required placeholders."""
        template = PROMPT_TEMPLATES["product_bot"]
        required_placeholders = ["context", "question"]
        
        for placeholder in required_placeholders:
            assert f"{{{placeholder}}}" in template, f"Template should contain '{{{placeholder}}}' placeholder"

if __name__ == "__main__":
    pytest.main([__file__])
