"""
🎨 Flex Message Templates for Nong Unjai
Templates สำหรับ Media Delivery Agent ส่งกลับหาคู่สนทนา

AGENT: Media Delivery Agent (Squad 4: Content Integrity & Delivery)
TASK: ส่งมอบสื่อ (Flex Messages) ให้กับผู้ใช้ผ่าน LINE

Usage:
    from flex_templates import FlexMessageBuilder
    
    builder = FlexMessageBuilder()
    video_card = builder.create_video_card({
        "title": "...",
        "full_url": "...",
        "thumbnail": "...",
        "score": 0.85
    })
"""
from typing import Dict, Any, Optional


class FlexMessageBuilder:
    """
    🎨 Builder สำหรับสร้าง LINE Flex Messages
    ใช้โดย Media Delivery Agent
    """
    
    @staticmethod
    def create_video_card(video: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎬 Video Card Template (แบบมีรูป thumbnail + ดาว 5 ดวง)
        
        ใช้สำหรับส่งคลิปวิดีโอพร้อม metadata
        """
        # Get video data with defaults
        thumbnail_url = video.get("thumbnail", "") or "https://via.placeholder.com/800x520?text=Video+Thumbnail"
        video_url = video.get("full_url", "") or video.get("clip_url", "")
        youtube_url = video.get("video_url", "") or video_url
        title = video.get("title", "คลิปหนุนใจจากน้องอุ่นใจ")[:100]
        score = video.get("score", 0)
        transcript = video.get("transcript", "")[:80]
        
        # Build rating text based on similarity score
        rating_text = f"ความตรงกัน: {score:.0%}"
        
        flex_message = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": thumbnail_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": video_url
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                        "color": "#111111"
                    },
                    {
                        "type": "text",
                        "text": transcript + "..." if transcript else "คลิปหนุนใจจาก FEBC Christian Media",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "md",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "FEBC Christian Media",
                        "size": "sm",
                        "color": "#999999",
                        "margin": "xs"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                            },
                            {
                                "type": "icon",
                                "size": "sm",
                                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                            },
                            {
                                "type": "text",
                                "text": rating_text,
                                "size": "sm",
                                "color": "#999999",
                                "margin": "md",
                                "flex": 0
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#FF6B6B",
                        "action": {
                            "type": "uri",
                            "label": "▶️ ดูวิดีโอ",
                            "uri": video_url
                        },
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "uri",
                            "label": "📺 ดูบน YouTube",
                            "uri": youtube_url
                        },
                        "height": "sm"
                    }
                ]
            }
        }
        
        return flex_message
    
    @staticmethod
    def create_video_nudge(video: Dict[str, Any]) -> Dict[str, Any]:
        """
        💡 Video Nudge Template (แบบชวนดู)
        
        ใช้เมื่อต้องการชวนผู้ใช้ดูวิดีโอแบบนุ่มนวล
        """
        video_url = video.get("full_url", "") or video.get("clip_url", "")
        title = video.get("title", "คลิปแนะนำ")[:50]
        reason = video.get("reason", "คลิปนี้น่าสนใจค่ะ")[:100]
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎬 คลิปแนะนำ",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FF6B6B"
                    },
                    {
                        "type": "text",
                        "text": title,
                        "size": "md",
                        "weight": "bold",
                        "margin": "md",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": reason,
                        "size": "sm",
                        "margin": "sm",
                        "wrap": True,
                        "color": "#666666"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูวิดีโอเลย",
                            "uri": video_url
                        },
                        "style": "primary",
                        "margin": "md",
                        "color": "#FF6B6B"
                    }
                ]
            }
        }
    
    @staticmethod
    def create_quiz_card(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📝 Quiz Card Template
        
        ใช้หลังผู้ใช้ดูวิดีโอจบ ให้ Academy Specialist ส่งควิซ
        """
        question = quiz_data.get("question", "คำถามหลังดูวิดีโอ")
        choices = quiz_data.get("choices", [])
        
        choice_buttons = []
        for i, choice in enumerate(choices[:4], 1):
            choice_buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": f"{i}. {choice[:20]}",
                    "text": f"ตอบ {i}"
                },
                "style": "secondary",
                "margin": "xs",
                "height": "sm"
            })
        
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📝 ควิซสนุกๆ",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF"
                    }
                ],
                "backgroundColor": "#FF6B6B"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": question,
                        "size": "md",
                        "wrap": True,
                        "margin": "md"
                    },
                    *choice_buttons
                ]
            }
        }
    
    @staticmethod
    def create_text_card(title: str, content: str) -> Dict[str, Any]:
        """
        📄 Text Card Template
        
        ใช้สำหรับส่งข้อความยาวๆ ในรูปแบบการ์ดสวยงาม
        """
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "lg",
                        "color": "#333333",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": content[:500] + "..." if len(content) > 500 else content,
                        "size": "sm",
                        "margin": "md",
                        "wrap": True,
                        "color": "#666666"
                    }
                ]
            }
        }
    
    @staticmethod
    def create_error_card(message: str = "ขออภัยค่ะ มีข้อผิดพลาดเล็กน้อย") -> Dict[str, Any]:
        """
        ⚠️ Error Card Template
        
        ใช้เมื่อเกิดข้อผิดพลาด
        """
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "😅 อุ๊ปส์!",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FF6B6B"
                    },
                    {
                        "type": "text",
                        "text": message,
                        "size": "sm",
                        "margin": "md",
                        "wrap": True
                    }
                ]
            }
        }


# Backward compatibility - keep old function names
def create_video_flex(video: Dict[str, Any]) -> Dict[str, Any]:
    """Backward compatible wrapper"""
    return FlexMessageBuilder.create_video_card(video)


def create_nudge_flex(video: Dict[str, Any]) -> Dict[str, Any]:
    """Backward compatible wrapper"""
    return FlexMessageBuilder.create_video_nudge(video)


if __name__ == "__main__":
    # Test
    builder = FlexMessageBuilder()
    
    test_video = {
        "title": "ตรุษจีนกับคริสเตียน",
        "full_url": "https://nongaunjai.febradio.org/static/clips/test.mp4",
        "thumbnail": "https://via.placeholder.com/800x520",
        "score": 0.823,
        "transcript": "การเฉลิมฉลองตรุษจีนในฐานะคริสเตียน",
        "video_url": "https://youtube.com/watch?v=test"
    }
    
    print("Testing FlexMessageBuilder...")
    card = builder.create_video_card(test_video)
    print(f"✅ Video card created: {card['type']}")
