from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .ai_service import AIService

class AIChatView(APIView):
    """
    POST API view to send prompts to the MediKal AI assistant.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        history = request.data.get('history', [])
        if not prompt or prompt.strip() == '':
            return Response(
                {"error": "A prompt parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response_text = AIService.generate_response(prompt, history)
            return Response(
                {
                    "prompt": prompt,
                    "response": response_text
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"AI service failed to process request: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
