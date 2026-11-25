# core/context_processors.py

def site_settings(request):
    """
    Provide global site settings or constants to all templates.
    """
    return {
        'site_name': 'EcoFarm Connect',
        'support_email': 'support@ecofarmconnect.com',
        # Add other global context data as needed
    }
