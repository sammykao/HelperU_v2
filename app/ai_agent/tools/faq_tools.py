from typing import List, Dict, Optional
from langchain.tools import tool

def _initialize_faq_database() -> Dict[str, Dict]:
        """Initialize FAQ database with common questions and answers"""
        return {
            "general": {
                "what_is_helperu": {
                    "question": "What is HelperU?",
                    "answer": """HelperU is a platform that connects people who need help with tasks to qualified student helpers in their area. Whether you need help moving, cleaning, handyman work, tutoring, or any other task, we connect you with reliable student helpers who can get the job done.

Our platform serves two main groups:
- **Clients**: People who need help with various tasks and projects
- **Student Helpers**: College students looking to earn money by helping others with tasks

We focus on creating a safe, reliable, and efficient marketplace where quality work meets fair compensation.""",
                    "tags": ["platform", "overview", "introduction"]
                },
                "how_it_works": {
                    "question": "How does HelperU work?",
                    "answer": """HelperU works as a simple three-step process:

**For Clients:**
1. **Post a Task**: Create a detailed task description with location, budget, and requirements
2. **Get Applications**: Receive applications from qualified student helpers in your area
3. **Chat & Hire**: Chat with helpers, hire and pay them seperately, and mark complete the task when the work is done so it is not searchable or available for new applications.

**For Student Helpers:**
1. **Sign Up & Verify**: Create your profile and complete identity verification
2. **Browse Tasks**: Search for available tasks that match your skills and location
3. **Apply & Earn**: Apply for tasks, complete the work, and get paid by the client.

**Key Features:**
- Location-based matching
- Identity verification for helpers
- Real-time messaging""",
                    "tags": ["process", "workflow", "steps"]
                },
                "safety_security": {
                    "question": "Is HelperU safe and secure?",
                    "answer": """Yes, HelperU prioritizes safety and security for all users:

**For Clients:**
- All helpers undergo email and phone verification for safety and college verification for accuracy.
- Hands on dispute resolution process, with a lenient approach to resolving issues as well as refunds.

**For Helpers:**
- Clear task descriptions and requirements
- Support for payment disputes
- Hands on dispute resolution process, with a lenient approach to resolving issues as well as unpaid tasks.

**Platform Security:**
- Encrypted data transmission
- Secure user authentication
- Privacy protection for personal information
- 24/7 customer support

**Trust Features:**
- Rating and review system
- Profile verification badges
- Task completion tracking
- Secure messaging system""",
                    "tags": ["safety", "security", "trust", "verification"]
                }
            },
            "pricing": {
                "task_posting_cost": {
                    "question": "How much does it cost to post a task?",
                    "answer": """HelperU offers flexible pricing plans for task posting:

**Free Plan:**
- 1 task postings per month
- Standard support

**Premium Plan ($9.99/month):**
- Unlimited task postings
- Priority customer support
- Task pro

**Payment Methods:**
- Credit/Debit cards
- PayPal
- Apple Pay
- Google Pay""",
                    "tags": ["pricing", "cost", "subscription", "fees"]
                },
                "helper_earnings": {
                    "question": "How much can helpers earn on HelperU?",
                    "answer": """Helper earnings on HelperU vary based on several factors:

**Average Earnings:**
- Part-time helpers: $50-$300/month
- Full-time helpers: $300-$800/month
- Top performers: $800-$1500/month

**Task Rate Examples:**
- Moving help: $25-$50/hour
- Cleaning: $20-$35/hour
- Tutoring: $30-$60/hour
- Handyman work: $30-$75/hour
- Pet sitting: $15-$30/hour

- Transparent fee structure""",
                    "tags": ["earnings", "money", "payment", "rates"]
                }
            },
            "registration": {
                "signup_process": {
                    "question": "How do I sign up for HelperU?",
                    "answer": """Signing up for HelperU is quick and easy:

**For Clients:**
1. Visit helperu.com and click "Sign Up"
3. Enter your phone number
4. Enter your phone to login and complete verification
5. Complete your profile with basic information
6. Start posting tasks immediately

**For Student Helpers:**
1. Visit helperu.com and click "Sign Up"
2. Enter your email and phone number
4. Verify your email and phone
5. Complete your profile with:
   - Personal information
   - College
   - Bio
   - Profile photo
7. Start browsing and applying for tasks

**Required Information:**
- Valid email address
- Phone number
- Full name
- Date of birth (for helpers)
- Location information

**Verification Process:**
- Email verification (instant)
- Phone verification (SMS code)
- Background check (optional, premium feature)""",
                    "tags": ["signup", "registration", "account", "verification"]
                },
                "profile_completion": {
                    "question": "How do I complete my profile?",
                    "answer": """Completing your HelperU profile is important for better matching:

**Client Profile Requirements:**
- Profile photo
- Contact information
- Preferred communication method
- Location and service area
- Task history (optional)

**Helper Profile Requirements:**
- Profile photo (required)
- Personal information
- Skills and experience
- Education background
- Availability schedule
- Hourly rates
- References (optional)
- Portfolio/work samples (optional)

**Profile Completion Tips:**
- Use a clear, professional photo
- Be specific about your skills
- Set realistic availability
- Include relevant experience
- Add a compelling bio
- Keep information up to date

**Profile Verification:**
- Identity verification (required for helpers)
- Skills assessment (optional)
- Reference checks (optional)
- Background check (premium feature)

**Profile Benefits:**
- Higher visibility in search results
- Better matching with tasks/clients
- Increased trust and credibility
- Higher earning potential
- Priority customer support""",
                    "tags": ["profile", "completion", "verification", "setup"]
                }
            },
            "tasks": {
                "task_types": {
                    "question": "What types of tasks can I post or find on HelperU?",
                    "answer": """HelperU supports a wide variety of tasks across multiple categories:

**Moving & Transportation:**
- Apartment/house moving
- Furniture assembly
- Delivery services
- Vehicle assistance
- Storage organization

**Cleaning & Maintenance:**
- House cleaning
- Deep cleaning
- Organizing services
- Laundry assistance
- Pet cleaning

**Academic & Tutoring:**
- Subject tutoring
- Homework help
- Essay writing assistance
- Test preparation
- Research assistance

**Handyman & Repairs:**
- Basic repairs
- Assembly services
- Installation help
- Maintenance tasks
- Small construction

**Pet & Animal Care:**
- Pet sitting
- Dog walking
- Pet grooming assistance
- Farm animal care
- Veterinary assistance

**Technology & IT:**
- Computer help
- Software assistance
- Website development
- Data entry
- Technical support

**Creative & Design:**
- Graphic design
- Photography
- Video editing
- Social media management
- Content creation

**Other Services:**
- Event planning
- Personal shopping
- Errand running
- Child care
- Elder care

**Task Requirements:**
- Must be legal and ethical
- Cannot involve dangerous activities
- Must be appropriate for student helpers
- Clear scope and requirements
- Fair compensation""",
                    "tags": ["tasks", "services", "categories", "types"]
                },
                "task_posting": {
                    "question": "How do I post a task on HelperU?",
                    "answer": """Posting a task on HelperU is straightforward:

**Step-by-Step Process:**
1. **Log in** to your HelperU account
2. Click **"Post a Task"** button
3. **Select category** (moving, cleaning, tutoring, etc.)
4. **Write description** with details about:
   - What needs to be done
   - Specific requirements
   - Location and timing
   - Budget range
5. **Set your budget** (hourly rate or fixed price)
6. **Choose location** and service area
7. **Add photos** (optional but recommended)
8. **Set deadline** for applications
9. **Review and post**

**Task Description Tips:**
- Be specific about requirements
- Include all necessary details
- Mention any special skills needed
- Specify timing and availability
- Include photos if relevant
- Set realistic budget expectations

**Budget Guidelines:**
- Research similar tasks in your area
- Consider task complexity
- Factor in helper experience level
- Be competitive but fair
- Include materials costs if applicable

**Posting Best Practices:**
- Respond quickly to applications
- Be clear about expectations
- Provide detailed instructions
- Set realistic deadlines
- Include contact information
- Be available for questions

**Task Management:**
- Review all applications
- Ask questions before hiring
- Communicate clearly with helper
- Provide feedback after completion
- Rate and review helper""",
                    "tags": ["posting", "task", "process", "guidelines"]
                }
            },
            "payments": {
                "payment_methods": {
                    "question": "What payment methods does HelperU accept?",
                    "answer": """HelperU offers multiple secure payment options:

**For Clients (Paying Helpers):**
- **All seperate**: You must pay the helper seperately for the work they do. 
- **Rules**: If you do not pay the helper, you will be banned from the platform.

**For Helpers (Receiving Payments):**
- **All seperate**: You must pay the helper seperately for the work they do. 
- **Rules**: If you do not pay the helper, you will be banned from the platform.
""",
                    "tags": ["payment", "money", "fees", "security"]
                },
                "refund_policy": {
                    "question": "What is HelperU's refund policy?",
                    "answer": """HelperU has a fair and transparent refund policy:

**Refund Process:**
1. **Report issue** within 48 hours of task completion
2. **Provide evidence** (photos, messages, etc.)
3. **Platform review** (1-3 business days)
4. **Refund decision** and processing
5. **Funds returned** to original payment method

**Refund Timeline:**
- **Credit card refunds:** 5-10 business days
- **PayPal refunds:** 1-3 business days
- **Bank transfer refunds:** 3-5 business days

**Customer Protection:**
- **HelperU Guarantee** for quality work
- **Insurance coverage** for certain tasks
- **24/7 support** for payment issues
- **Transparent dispute process**""",
                    "tags": ["refund", "policy", "dispute", "protection"]
                }
            },
            "support": {
                "contact_support": {
                    "question": "How do I contact HelperU support?",
                    "answer": """HelperU provides multiple ways to get support:

**24/7 Customer Support:**
- **Live Chat:** Available on website and mobile app
- **Email:** info@helperu.com

**Support Hours:**
- **General Support:** 24/7
- **Phone Support:** 8 AM - 8 PM EST
- **Priority Support:** Available for premium users
- **Emergency Support:** Available for urgent issues

**Support Categories:**
- **Account Issues:** Login, verification, profile
- **Task Problems:** Posting, matching, completion
- **Payment Issues:** Billing, refunds, disputes
- **Technical Support:** App issues, website problems
- **Safety Concerns:** Trust and safety issues

**Response Times:**
- **Live Chat:** Immediate response
- **Email:** Within 4 hours
- **Phone:** Immediate during business hours
- **Help Center:** Self-service available 24/7

**Premium Support:**
- **Priority Support:** Faster response times
- **Dedicated Support:** Assigned support representative
- **Extended Hours:** Extended phone support
- **Custom Solutions:** Tailored assistance

**Self-Service Options:**
- **Help Center:** Comprehensive FAQ and guides
- **Video Tutorials:** Step-by-step instructions
- **Community Forum:** User discussions and tips
- **Knowledge Base:** Detailed documentation

**Emergency Contacts:**
- **Safety Issues:** safety@helperu.com
- **Legal Matters:** legal@helperu.com
- **Press Inquiries:** press@helperu.com""",
                    "tags": ["support", "contact", "help", "customer_service"]
                },
                "troubleshooting": {
                    "question": "What should I do if I have a problem?",
                    "answer": """Here's how to resolve common issues on HelperU:

**Common Issues and Solutions:**

**Account Problems:**
- **Can't log in:** Reset password or contact support
- **Verification issues:** Check email/phone or re-verify
- **Profile not updating:** Clear cache or try different browser
- **Account suspended:** Contact support for review

**Task Issues:**
- **No helpers applying:** Check budget, description, and location
- **Helper no-show:** Report immediately and request refund
- **Poor quality work:** Document issues and contact support
- **Task cancellation:** Review cancellation policy

**Payment Problems:**
- **Payment declined:** Check card details or try different method
- **Missing payment:** Check payment history or contact support
- **Refund not received:** Allow 5-10 business days then contact support
- **Wrong amount charged:** Contact support with transaction details

**Technical Issues:**
- **App not working:** Update app or try website version
- **Website errors:** Clear cache or try different browser
- **Messages not sending:** Check internet connection
- **Photos not uploading:** Check file size and format

**Safety Concerns:**
- **Inappropriate behavior:** Report immediately to safety@helperu.com
- **Safety concerns:** Contact support or emergency services
- **Fraud attempts:** Report to support with evidence
- **Trust issues:** Use platform messaging and payment

**Escalation Process:**
1. **Try self-service** options first
2. **Contact support** with clear description
3. **Provide evidence** (screenshots, messages, etc.)
4. **Follow up** if no response within expected time
5. **Escalate** to supervisor if needed

**Prevention Tips:**
- **Read policies** and terms of service
- **Communicate clearly** with helpers/clients
- **Document everything** (messages, photos, payments)
- **Use platform features** (messaging, payments, reviews)
- **Report issues** promptly""",
                    "tags": ["troubleshooting", "problems", "solutions", "help"]
                }
            }
        }
    
@tool
def search_faq(query: str, category: Optional[str] = None) -> List[Dict]:
        """Search for FAQ entries based on a query and optional category.
        
        This function allows AI agents to find relevant FAQ information based on user questions.
        It searches through the FAQ database to find the most relevant answers for common
        questions about the HelperU platform, including pricing, safety, registration,
        tasks, payments, and support.
        
        Args:
            query (str): The search query to find relevant FAQ entries. This should be
                        a natural language question or topic the user is asking about.
                        Examples: "How much does it cost?", "Is it safe?", "How do I sign up?"
            
            category (str, optional): The specific category to search within. If provided,
                                     only searches within that category. Valid categories:
                                     "general", "pricing", "registration", "tasks", 
                                     "payments", "support". If None, searches all categories.
        
        Returns:
            List[Dict]: A list of FAQ entries that match the query, each containing:
                       - question: The FAQ question
                       - answer: The detailed answer
                       - tags: List of relevant tags
                       - category: The category this FAQ belongs to
        
        Example:
            >>> results = search_faq("How much does it cost to post a task?")
            >>> results = search_faq("safety", category="general")
        """
        query_lower = query.lower()
        results = []
        
        # Determine which categories to search
        categories_to_search = [category] if category else faq_database.keys()
        
        for cat in categories_to_search:
            if cat not in faq_database:
                continue
                
            for faq_id, faq_data in faq_database[cat].items():
                # Check if query matches question, answer, or tags
                question_match = query_lower in faq_data["question"].lower()
                answer_match = query_lower in faq_data["answer"].lower()
                tag_match = any(query_lower in tag.lower() for tag in faq_data["tags"])
                
                if question_match or answer_match or tag_match:
                    results.append({
                        "question": faq_data["question"],
                        "answer": faq_data["answer"],
                        "tags": faq_data["tags"],
                        "category": cat
                    })
        
        return results[:5]  # Limit to top 5 results
    
@tool
def get_faq_by_category(category: str) -> List[Dict]:
        """Get all FAQ entries for a specific category.
        
        This function allows AI agents to retrieve all FAQ entries within a specific
        category. This is useful when users want comprehensive information about
        a particular aspect of the platform, such as all pricing information or
        all registration steps.
        
        Args:
            category (str): The category to retrieve FAQ entries from. Valid categories:
                           "general", "pricing", "registration", "tasks", "payments", "support"
        
        Returns:
            List[Dict]: A list of all FAQ entries in the specified category, each containing:
                       - question: The FAQ question
                       - answer: The detailed answer
                       - tags: List of relevant tags
                       - category: The category this FAQ belongs to
        
        Raises:
            ValueError: If the category doesn't exist in the FAQ database
        
        Example:
            >>> pricing_faqs = get_faq_by_category("pricing")
            >>> registration_faqs = get_faq_by_category("registration")
        """
        if category not in faq_database:
            raise ValueError(f"Category '{category}' not found. Available categories: {list(faq_database.keys())}")
        
        results = []
        for faq_id, faq_data in faq_database[category].items():
            results.append({
                "question": faq_data["question"],
                "answer": faq_data["answer"],
                "tags": faq_data["tags"],
                "category": category
            })
        
        return results
    
@tool
def get_popular_faqs(limit: int = 5) -> List[Dict]:
        """Get the most popular FAQ entries based on common user questions.
        
        This function returns the most frequently asked questions and their answers.
        These are typically the questions that new users ask most often, covering
        the basics of how the platform works, safety, pricing, and getting started.
        
        Args:
            limit (int): The maximum number of popular FAQs to return. Default is 5,
                        maximum is 10 to keep responses manageable.
        
        Returns:
            List[Dict]: A list of popular FAQ entries, each containing:
                       - question: The FAQ question
                       - answer: The detailed answer
                       - tags: List of relevant tags
                       - category: The category this FAQ belongs to
        
        Example:
            >>> popular = get_popular_faqs(3)
        """
        # Define popular FAQs based on common user questions
        popular_faq_ids = [
            ("general", "what_is_helperu"),
            ("general", "how_it_works"),
            ("pricing", "task_posting_cost"),
            ("registration", "signup_process"),
            ("general", "safety_security"),
            ("payments", "payment_methods"),
            ("tasks", "task_types"),
            ("support", "contact_support")
        ]
        
        results = []
        for category, faq_id in popular_faq_ids[:limit]:
            if category in faq_database and faq_id in faq_database[category]:
                faq_data = faq_database[category][faq_id]
                results.append({
                    "question": faq_data["question"],
                    "answer": faq_data["answer"],
                    "tags": faq_data["tags"],
                    "category": category
                })
        
        return results
    
@tool
def get_faq_categories(self) -> List[str]:
    """Get a list of all available FAQ categories.
    
    This function returns all the categories available in the FAQ database.
    This is useful for helping users understand what types of information
    are available and for navigation purposes.
    
    Returns:
        List[str]: A list of all available FAQ categories:
                    ["general", "pricing", "registration", "tasks", "payments", "support"]
    
    Example:
        >>> categories = get_faq_categories()
    """
    return list(faq_database.keys())

# Global FAQ database initialization
faq_database = _initialize_faq_database()
