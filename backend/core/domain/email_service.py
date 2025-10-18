import datetime

import structlog
from sib_api_v3_sdk import ApiClient, Configuration, SendSmtpEmail, TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException

from core.domain.schemas import ParsedNewsBasic

logger = structlog.get_logger()


class EmailNewsletterService:
    def __init__(self, brevo_api_key: str):
        self.brevo_api_key = brevo_api_key
        self.configuration = Configuration()
        self.configuration.api_key["api-key"] = brevo_api_key
        self.api_client = ApiClient(self.configuration)
        self.api_instance = TransactionalEmailsApi(self.api_client)
        self.sender_email = "noreply@tvujnovinar.cz"
        self.sender_name = "Tvůj Novinář"
        logger.info("EmailNewsletterService initialized")

    def _truncate_content(self, content: str, word_count: int = 30) -> str:
        """
        Truncate content to first N words and add ellipsis.

        Args:
            content: Full article text
            word_count: Number of words to display

        Returns:
            Truncated text with ellipsis
        """
        if not content:
            return "Obsah není k dispozici."

        words = content.split()

        if len(words) <= word_count:
            return content

        truncated = " ".join(words[:word_count])
        return f"{truncated}..."

    def _get_article_word(self, count: int) -> str:
        """Returns correct Czech form of 'article' based on count."""
        _SINGULAR_COUNT = 1
        _PAUCAL_MIN = 2
        _PAUCAL_MAX = 4
        if count == _SINGULAR_COUNT:
            return "nový článek"
        elif _PAUCAL_MIN <= count <= _PAUCAL_MAX:
            return "nové články"
        else:
            return "nových článků"

    def _generate_article_html(self, article: ParsedNewsBasic, preview_words: int = 30) -> str:
        """
        Generate HTML for a single article.

        Args:
            article: ParsedNewsBasic object
            preview_words: Number of words to show in preview

        Returns:
            HTML string for the article
        """
        title = article.title
        url = f"https://tvujnovinar.cz/article/{article.id}"
        content = article.description
        category = article.topic.name if article.topic else "Nedostupný"
        preview = self._truncate_content(content, preview_words)

        return f"""
        <div style="margin-bottom: 20px; padding: 25px; background-color: #ffffff; border:
        1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 0.5px;">
                {category}
            </div>
            <h2 style="margin: 0 0 10px 0; font-size: 20px; color: #1e293b; font-weight: 700; line-height: 1.4;">
                <a href="{url}" style="color: #1e293b; text-decoration: none;">
                    {title}
                </a>
            </h2>
            <p style="margin: 0 0 15px 0; font-size: 14px; color: #64748b; line-height: 1.6;">
                {preview}
            </p>
            <a href="{url}"
               style="display: inline-block; color: #ef4444; text-decoration: none;
                      font-size: 14px; font-weight: 600;">
                Přečíst celý článek →
            </a>
        </div>
        """

    def _generate_articles_html(self, articles: list[ParsedNewsBasic], preview_words: int = 30) -> str:
        """Generate HTML for all articles."""
        articles_html = ""

        for article in articles:
            articles_html += self._generate_article_html(article, preview_words)

        return articles_html

    def generate_daily_news_email(
        self,
        articles: list[ParsedNewsBasic],
        prompt_description: str,
        user_name: str = "Uživateli",
        preview_words: int = 30,
    ) -> str:
        """
        Generate HTML email with daily news overview.

        Args:
            articles: List of ParsedNewsBasic objects
            user_name: User's name
            prompt_description: Description of user's topic/prompt
            preview_words: Number of words from content to display (default 30)

        Returns:
            HTML string ready to send via email
        """
        logger.info(f"Generating email for user {user_name} with {len(articles)} articles")
        logger.debug(f"Prompt description: {prompt_description}, preview words: {preview_words}")

        previous_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d. %m. %Y")
        article_count = len(articles)

        html_template = f"""
        <!DOCTYPE html>
        <html lang="cs">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Denní přehled zpráv</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial,
        sans-serif; background-color: #f1f5f9;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color:
                        #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                            <!-- Hlavička -->
                            <tr>
                                <td style="background-color: #1e293b; color: #ffffff; padding: 30px;
                                text-align: center;">
                                    <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Tvůj Novinář</h1>
                                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.8;">
                                    Denní přehled zpráv • {previous_date}</p>
                                </td>
                            </tr>

                            <!-- Úvodní text -->
                            <tr>
                                <td style="padding: 30px;">
                                    <p style="margin: 0 0 20px 0; font-size: 16px; color: #333333;">
                                        Pěkný den!
                                    </p>
                                    <p style="margin: 0 0 20px 0; font-size: 14px; color: #666666; line-height: 1.6;">
                                        Náš AI novinář vybral speciálně pro tebe <strong>{article_count}
                                        {self._get_article_word(article_count)}</strong>
                                        na míru podle zadaného tématu <strong>{prompt_description}</strong>.
                                        Výběr šitý na míru – jako bys měl vlastního redaktora!
                                    </p>
                                </td>
                            </tr>

                            <!-- Články -->
                            <tr>
                                <td style="padding: 0 30px 30px 30px;">
                                    {self._generate_articles_html(articles, preview_words)}
                                </td>
                            </tr>

                            <!-- Závěr -->
                            <tr>
                                <td style="padding: 30px; background-color: #f8f9fa; border-top: 1px solid #e9ecef;">
                                    <p style="margin: 0; font-size: 14px; color: #666666; text-align: center;">
                                        Tento přehled byl vytvořen na základě tvého nastaveného tématu:
                                        <em>{prompt_description}</em>
                                    </p>
                                </td>
                            </tr>

                            <!-- Patička -->
                            <tr>
                                <td style="padding: 20px; text-align: center; font-size: 12px; color: #999999;">
                                    <p style="margin: 0;">
                                    Pokud chceš změnit svůj prompt, nebo zrušit newsletter, můžeš to udělat na stránce:
                                    https://tvujnovinar.cz/feed
                                    </p>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        logger.info(f"Successfully generated email HTML for {article_count} articles")
        return html_template

    async def send_newsletter(
        self,
        recipient_email: str,
        articles: list[ParsedNewsBasic],
        prompt_description: str,
        user_name: str = "Uživateli",
        preview_words: int = 30,
    ) -> bool:
        """
        Generate and send newsletter via Brevo.

        Args:
            recipient_email: Email address of the recipient
            articles: List of ParsedNewsBasic objects
            user_name: User's name
            prompt_description: Description of user's topic/prompt
            preview_words: Number of words to show in preview

        Returns:
            True if email was sent successfully

        Raises:
            ApiException: If Brevo API call fails
        """
        logger.info(f"Sending newsletter to {recipient_email} with {len(articles)} articles")

        # Generate email HTML
        html_content = self.generate_daily_news_email(
            articles=articles,
            user_name=user_name,
            prompt_description=prompt_description,
            preview_words=preview_words,
        )

        # Prepare email
        subject = (
            f"Denní přehled zpráv - {(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d. %m. %Y')}"
        )

        send_smtp_email = SendSmtpEmail(
            to=[{"email": recipient_email, "name": user_name}],
            sender={"email": self.sender_email, "name": self.sender_name},
            subject=subject,
            html_content=html_content,
        )

        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {recipient_email}. Message ID: {api_response.message_id}")
            logger.debug(f"Brevo API response: {api_response}")
            return True

        except ApiException as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            raise
