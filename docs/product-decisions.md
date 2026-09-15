# Product decisions

## Customer problem

Hotel guests need dependable answers while planning or during a stay, without waiting in a front-desk queue. The assistant focuses on high-frequency questions that can be answered from published hotel information and on the room-search journey where inaccurate answers are especially costly.

## Guest journey

1. A guest opens the hotel page and sees a concise welcome.
2. They choose a suggested question or write one in chat.
3. The assistant responds from the hotel knowledge base.
4. The guest can naturally ask a follow-up, such as breakfast after discussing rooms.
5. For dates and party size, they use the structured availability form.
6. They compare returned room cards or receive an honest no-availability result.

## UX choices

- Chat suits short, varied concierge questions and preserves the current session's context.
- Quick actions reduce blank-page friction and make supported capabilities visible.
- The assistant is a focused conversation drawer on desktop and a floating chat surface on mobile: it stays out of the way while guests browse, then opens with a welcome, assistant identity, online state, and popular-question chips.
- Assistant answers show retrieved sources when a response comes from indexed hotel material, making the experience easier to trust and review.
- Dates and guests use native controls because they are precise, accessible, and easy to validate before a request is sent.
- Loading disables duplicate requests and typing feedback confirms that the request is in progress.
- Errors use plain language with retry and dismiss controls; raw server details are never rendered.
- The two-column desktop layout keeps chat and availability visible together, while mobile naturally stacks them.
- Hotel staff get a separate operations surface at `/admin`, keeping ingestion and live-inventory editing out of the guest flow.

## How usefulness would be measured

- Answer success rate for the eight most common hotel questions, checked against a reviewed answer set.
- Availability task completion rate from opening the room finder to receiving a valid result.
- Follow-up completion rate, measuring whether a guest can ask a second question without restarting.
- Grounded-answer coverage and unsupported-answer rate, sampled from source citations and human review.
- Median response time, provider failure rate, and fallback rate.
- Guest satisfaction after a resolved chat, plus front-desk deflection for questions the assistant is designed to handle.
