class ScoreCalculator:
    @staticmethod
    def calculate_overall(breakdown):
        """Calculates weighted average if overall_score is missing or needs validation"""
        if not breakdown:
            return 0
        
        scores = [item['score'] for item in breakdown.values()]
        return sum(scores) / len(scores) if scores else 0

    @staticmethod
    def get_grade(score):
        if score >= 90: return 'A'
        if score >= 80: return 'B'
        if score >= 70: return 'C'
        if score >= 60: return 'D'
        return 'F'

    @staticmethod
    def get_severity_color(severity):
        colors = {
            'high': 'red',
            'medium': 'yellow',
            'low': 'blue'
        }
        return colors.get(severity.lower(), 'gray')
